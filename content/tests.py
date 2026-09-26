from django.test import TestCase
from django.urls import reverse

from .models import (
    DigitalExperiencesSection,
    FaqItem,
    FooterTopSection,
    HeroBadge,
    HeroSection,
    IndustriesSection,
    Industry,
    Package,
    Project,
    Template,
    SiteSettings,
    SocialLink,
    Stat,
    TeamMember,
    YourIdeaSection,
    split_lines,
)


class ContentApiTests(TestCase):
    def setUp(self):
        self.url = reverse("site-content")
        # Migration 0006 seeds the eight built-in templates into the test
        # database too; clear them so these fixtures stand alone.
        Template.objects.all().delete()
        SiteSettings.objects.create(name="ORIK Webcraft", description="We build websites.", email="hi@orik.test")
        self.template = Template.objects.create(
            key="restaurant",
            name="Saffron Table",
            domain="saffrontable.demo",
            headline="Fresh flavours, served daily",
            subline="Book a table or order online in seconds.",
            cta="Book a table",
            nav="Menu\nBook\nContact",
            cards="Breakfast\nLunch\nDinner",
        )
        Industry.objects.create(
            name="Restaurants & Cafes",
            pitch="Show your menu.",
            features="Digital menu\nTable booking\n\n  Google Maps  ",
            template_industry=self.template,
            order=0,
        )
        Package.objects.create(name="Starter", tagline="First site.", features="One page\nMobile friendly", order=0)
        FaqItem.objects.create(question="How long?", answer="A few weeks.", order=0)

    def get(self):
        return self.client.get(self.url).json()

    def test_payload_has_every_section(self):
        data = self.get()
        expected = {
            "site",
            "industriesSection",
            "footerTop",
            "templates",
            "hero",
            "yourIdea",
            "digitalExperiences",
            "stats",
            "problems",
            "industries",
            "projects",
            "processSteps",
            "packages",
            "team",
            "testimonials",
            "faqs",
            "footerBottom",
        }
        self.assertEqual(set(data), expected)

    def test_features_become_lists_and_blank_lines_are_dropped(self):
        industry = self.get()["industries"][0]
        self.assertEqual(industry["features"], ["Digital menu", "Table booking", "Google Maps"])

    def test_slug_is_generated_and_matches_the_frontend_rule(self):
        # frontend industrySlug("Restaurants & Cafes") produces the same value.
        self.assertEqual(self.get()["industries"][0]["slug"], "restaurants-cafes")

    def test_industry_carries_its_whole_template(self):
        template = self.get()["industries"][0]["template"]
        self.assertEqual(template["name"], "Saffron Table")
        self.assertEqual(template["domain"], "saffrontable.demo")
        self.assertEqual(template["nav"], ["Menu", "Book", "Contact"])
        self.assertEqual(template["cards"], ["Breakfast", "Lunch", "Dinner"])

    def test_unpublished_rows_are_hidden(self):
        FaqItem.objects.create(question="Hidden?", answer="Yes.", is_published=False, order=1)
        questions = [item["question"] for item in self.get()["faqs"]]
        self.assertEqual(questions, ["How long?"])

    def test_order_field_drives_the_sequence(self):
        Stat.objects.create(value="2", label="second", order=2)
        Stat.objects.create(value="1", label="first", order=1)
        self.assertEqual([s["value"] for s in self.get()["stats"]], ["1", "2"])

    def test_social_links_without_a_url_are_hidden(self):
        SocialLink.objects.create(platform="whatsapp", label="WhatsApp", href="https://wa.me/123", order=0)
        SocialLink.objects.create(platform="instagram", label="Instagram", href="", order=1)

        platforms = [s["platform"] for s in self.get()["site"]["socials"]]
        self.assertEqual(platforms, ["whatsapp"])

    def test_blank_contact_fields_are_omitted(self):
        contact = self.get()["site"]["contact"]
        self.assertEqual(contact, {"email": "hi@orik.test"})

    def test_site_falls_back_to_defaults_when_unconfigured(self):
        SiteSettings.objects.all().delete()
        self.assertEqual(self.get()["site"]["name"], "ORIK Webcraft")

    def test_empty_section_returns_an_empty_list(self):
        self.assertEqual(self.get()["testimonials"], [])

    def test_per_model_endpoint_also_works(self):
        response = self.client.get("/api/content/faqs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["question"], "How long?")

    def test_content_is_read_only(self):
        self.assertEqual(self.client.post("/api/content/faqs/", {"question": "x", "answer": "y"}).status_code, 405)


class FooterTopTests(TestCase):
    def setUp(self):
        self.url = reverse("site-content")
        self.section = FooterTopSection.objects.create()

    def payload(self):
        return self.client.get(self.url).json()["footerTop"]

    def test_defaults_match_the_current_copy(self):
        data = self.payload()
        self.assertEqual(data["left"]["heading"], "Business first, with personal support.")
        self.assertEqual(data["left"]["ctaLabel"], "Our process")
        self.assertEqual(data["right"]["eyebrow"], "Why ORIK Webcraft")
        self.assertEqual(data["right"]["ctaHref"], "/work")

    def test_right_heading_keeps_its_line_break(self):
        self.assertIn("\n", self.payload()["right"]["heading"])

    def test_missing_images_are_empty_so_the_frontend_keeps_its_own(self):
        data = self.payload()
        self.assertEqual(data["left"]["image"], "")
        self.assertEqual(data["right"]["image"], "")

    def test_edits_are_served(self):
        self.section.left_heading = "Edited left."
        self.section.right_cta_label = "Edited button"
        self.section.save()

        data = self.payload()
        self.assertEqual(data["left"]["heading"], "Edited left.")
        self.assertEqual(data["right"]["ctaLabel"], "Edited button")

    def test_payload_survives_an_unconfigured_section(self):
        FooterTopSection.objects.all().delete()
        # An unsaved default still carries the built-in copy.
        self.assertEqual(self.payload()["left"]["ctaHref"], "/process")

    def test_second_section_is_refused(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            FooterTopSection().clean()

    def test_uploaded_image_requires_alt_text(self):
        from django.core.exceptions import ValidationError
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.section.left_image = SimpleUploadedFile("p.jpg", b"x", content_type="image/jpeg")
        self.section.left_image_alt = "  "
        with self.assertRaises(ValidationError) as caught:
            self.section.clean()
        self.assertIn("left_image_alt", caught.exception.message_dict)


class TemplateTests(TestCase):
    def setUp(self):
        self.url = reverse("site-content")
        Template.objects.all().delete()
        self.template = Template.objects.create(
            key="restaurant", name="Saffron Table", domain="saffrontable.demo",
            headline="Fresh flavours, served daily", subline="Book a table.",
            cta="Book a table", nav="Menu\nBook\nContact", cards="Breakfast\nLunch\nDinner",
        )

    def test_lists_are_split_and_trimmed(self):
        self.template.nav = "  Menu  \n\n Book \n"
        self.assertEqual(self.template.nav_list, ["Menu", "Book"])

    def test_colours_default_to_the_brand_green(self):
        payload = self.client.get(self.url).json()["templates"][0]
        self.assertEqual(payload["accent"], "#008454")
        self.assertEqual(payload["accentDark"], "#00683e")

    def test_one_template_serves_an_industry_and_a_project(self):
        Industry.objects.create(name="Retail", pitch="p", features="f", template_industry=self.template)
        Project.objects.create(
            title="Urban Thread", category="Shop", description="d", features="f", template_project=self.template
        )

        data = self.client.get(self.url).json()
        self.assertEqual(data["industries"][0]["template"]["domain"], "saffrontable.demo")
        self.assertEqual(data["projects"][0]["template"]["domain"], "saffrontable.demo")

    def test_editing_a_template_updates_every_user(self):
        Industry.objects.create(name="Retail", pitch="p", features="f", template_industry=self.template)
        Project.objects.create(
            title="Urban Thread", category="Shop", description="d", features="f", template_project=self.template
        )

        self.template.domain = "changed.demo"
        self.template.save()

        data = self.client.get(self.url).json()
        self.assertEqual(data["industries"][0]["template"]["domain"], "changed.demo")
        self.assertEqual(data["projects"][0]["template"]["domain"], "changed.demo")

    def test_deleting_a_template_leaves_its_users_standing(self):
        industry = Industry.objects.create(name="Retail", pitch="p", features="f", template_industry=self.template)
        self.template.delete()
        industry.refresh_from_db()

        self.assertIsNone(industry.template_industry)
        self.assertEqual(Industry.objects.count(), 1)

    def test_industry_without_a_template_serialises_as_null(self):
        Industry.objects.create(name="Retail", pitch="p", features="f")
        self.assertIsNone(self.client.get(self.url).json()["industries"][0]["template"])

    def test_key_is_unique(self):
        from django.db.utils import IntegrityError

        with self.assertRaises(IntegrityError):
            Template.objects.create(
                key="restaurant", name="Clash", domain="clash.demo", headline="h", subline="s",
                cta="c", nav="a", cards="b",
            )


class IndustriesSectionTests(TestCase):
    def setUp(self):
        self.url = reverse("site-content")
        IndustriesSection.objects.create()

    def payload(self):
        return self.client.get(self.url).json()["industriesSection"]

    def test_defaults_match_the_current_copy(self):
        data = self.payload()
        self.assertEqual(data["heading"], "Built for businesses like yours.")
        self.assertEqual(data["linkLabel"], "Start a project")
        self.assertEqual(data["footnoteLabel"], "Every demo we build is")

    def test_footnote_items_become_a_list(self):
        self.assertEqual(self.payload()["footnoteItems"], ["Mobile friendly", "Fast & modern", "Business focused"])

    def test_second_section_is_refused(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            IndustriesSection(heading="Another").clean()


class DigitalExperiencesTests(TestCase):
    def setUp(self):
        self.url = reverse("site-content")
        self.section = DigitalExperiencesSection.objects.create(
            heading="Digital experiences built\nfor modern business."
        )

    def payload(self):
        return self.client.get(self.url).json()["digitalExperiences"]

    def test_copy_is_served_with_camelcase_keys(self):
        data = self.payload()
        self.assertEqual(data["linkLabel"], "Get a free consultation")
        self.assertEqual(data["linkHref"], "/contact")

    def test_heading_keeps_its_line_break(self):
        self.assertIn("\n", self.payload()["heading"])

    def test_stats_belong_to_the_section(self):
        Stat.objects.create(section=self.section, value="10+", label="projects", order=0)
        self.assertEqual([s.value for s in self.section.stats.all()], ["10+"])

    def test_deleting_the_section_takes_its_stats(self):
        Stat.objects.create(section=self.section, value="10+", label="projects")
        self.section.delete()
        self.assertEqual(Stat.objects.count(), 0)

    def test_stats_still_serialise_at_the_top_level(self):
        Stat.objects.create(section=self.section, value="10+", label="projects", order=0)
        values = [s["value"] for s in self.client.get(self.url).json()["stats"]]
        self.assertEqual(values, ["10+"])

    def test_payload_survives_an_unconfigured_section(self):
        DigitalExperiencesSection.objects.all().delete()
        self.assertEqual(self.payload()["heading"], "")

    def test_second_section_is_refused(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            DigitalExperiencesSection(heading="Another").clean()


class YourIdeaTests(TestCase):
    def setUp(self):
        self.url = reverse("site-content")
        self.section = YourIdeaSection.objects.create(
            heading="Your business deserves more\nthan just a social media page.",
            closing_text="We turn those problems into a simple digital experience.",
        )

    def payload(self):
        return self.client.get(self.url).json()["yourIdea"]

    def test_copy_is_served_with_camelcase_keys(self):
        data = self.payload()
        self.assertEqual(data["closingText"], "We turn those problems into a simple digital experience.")
        self.assertEqual(data["ctaLabel"], "Get a free consultation")
        self.assertEqual(data["ctaHref"], "/contact")

    def test_heading_keeps_its_line_break(self):
        # The frontend renders this with whitespace-pre, so the newline is content.
        self.assertIn("\n", self.payload()["heading"])

    def test_cards_belong_to_the_section(self):
        from .models import Problem

        Problem.objects.create(section=self.section, title="No website", description="…", order=0)
        self.assertEqual([p.title for p in self.section.problems.all()], ["No website"])

    def test_deleting_the_section_takes_its_cards(self):
        from .models import Problem

        Problem.objects.create(section=self.section, title="Gone", description="…")
        self.section.delete()
        self.assertEqual(Problem.objects.count(), 0)

    def test_cards_still_serialise_at_the_top_level(self):
        from .models import Problem

        Problem.objects.create(section=self.section, title="No website", description="…", order=0)
        titles = [p["title"] for p in self.client.get(self.url).json()["problems"]]
        self.assertEqual(titles, ["No website"])

    def test_payload_survives_an_unconfigured_section(self):
        YourIdeaSection.objects.all().delete()
        self.assertEqual(self.payload()["heading"], "")

    def test_second_section_is_refused(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            YourIdeaSection(heading="Another", closing_text="x").clean()


class HeroSectionTests(TestCase):
    def setUp(self):
        self.url = reverse("site-content")
        self.hero = HeroSection.objects.create(
            heading="We build websites.",
            subheading="Modern websites and more.",
            qualities="Mobile\n\n  Fast  \nModern",
        )

    def hero_payload(self):
        return self.client.get(self.url).json()["hero"]

    def test_hero_copy_is_served(self):
        payload = self.hero_payload()
        self.assertEqual(payload["heading"], "We build websites.")
        self.assertEqual(payload["subheading"], "Modern websites and more.")

    def test_qualities_become_a_trimmed_list(self):
        self.assertEqual(self.hero_payload()["qualities"], ["Mobile", "Fast", "Modern"])

    def test_missing_image_is_empty_so_the_frontend_keeps_its_own(self):
        self.assertEqual(self.hero_payload()["image"], "")

    def test_badges_follow_their_order(self):
        HeroBadge.objects.create(hero=self.hero, label="Second", icon="seo", order=2)
        HeroBadge.objects.create(hero=self.hero, label="First", icon="mobile", order=1)

        self.assertEqual([b["label"] for b in self.hero_payload()["badges"]], ["First", "Second"])

    def test_unpublished_badge_is_hidden(self):
        HeroBadge.objects.create(hero=self.hero, label="Shown", icon="seo", order=1)
        HeroBadge.objects.create(hero=self.hero, label="Hidden", icon="seo", order=2, is_published=False)

        self.assertEqual([b["label"] for b in self.hero_payload()["badges"]], ["Shown"])

    def test_deleting_the_hero_takes_its_badges(self):
        HeroBadge.objects.create(hero=self.hero, label="Gone", icon="seo")
        self.hero.delete()
        self.assertEqual(HeroBadge.objects.count(), 0)

    def test_payload_survives_an_unconfigured_hero(self):
        # The frontend falls back per field, but the endpoint must not 500.
        HeroSection.objects.all().delete()
        payload = self.hero_payload()
        self.assertEqual(payload["heading"], "")
        self.assertEqual(payload["badges"], [])

    def test_second_hero_is_refused(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            HeroSection(heading="Another", subheading="x").clean()

    def test_uploaded_image_requires_alt_text(self):
        from django.core.exceptions import ValidationError
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.hero.image = SimpleUploadedFile("hero.jpg", b"not-a-real-image", content_type="image/jpeg")
        self.hero.image_alt = "   "
        with self.assertRaises(ValidationError) as caught:
            self.hero.clean()
        self.assertIn("image_alt", caught.exception.message_dict)

class TeamMemberTests(TestCase):
    def setUp(self):
        self.member = TeamMember.objects.create(name="Asha Rai", role="Designer", order=0)

    def test_member_with_no_links_reports_none(self):
        self.assertEqual(self.member.links, [])

    def test_whatsapp_number_becomes_a_wa_me_url(self):
        self.member.whatsapp = "+977 9800000000"
        self.assertEqual(
            [link for link in self.member.links if link["platform"] == "whatsapp"],
            [{"platform": "whatsapp", "href": "https://wa.me/9779800000000"}],
        )

    def test_email_becomes_a_mailto_link(self):
        self.member.email = "asha@orik.test"
        self.assertIn({"platform": "email", "href": "mailto:asha@orik.test"}, self.member.links)

    def test_blank_socials_are_omitted_and_order_is_stable(self):
        self.member.linkedin = "https://linkedin.com/in/asha"
        self.member.instagram = "https://instagram.com/asha"
        self.assertEqual([link["platform"] for link in self.member.links], ["linkedin", "instagram"])

    def test_missing_photo_serialises_as_empty_string(self):
        payload = self.client.get(reverse("site-content")).json()["team"][0]
        self.assertEqual(payload["photo"], "")
        self.assertEqual(payload["name"], "Asha Rai")

    def test_unpublished_member_is_hidden(self):
        TeamMember.objects.create(name="Hidden", role="Dev", is_published=False, order=1)
        names = [m["name"] for m in self.client.get(reverse("site-content")).json()["team"]]
        self.assertEqual(names, ["Asha Rai"])


class ContentModelTests(TestCase):
    def test_split_lines_trims_and_drops_blanks(self):
        self.assertEqual(split_lines("  a  \n\n b \n"), ["a", "b"])
        self.assertEqual(split_lines(""), [])
        self.assertEqual(split_lines(None), [])

    def test_slug_is_left_alone_once_set(self):
        industry = Industry.objects.create(name="Real Estate", pitch="p", features="f")
        industry.name = "Property"
        industry.save()
        self.assertEqual(industry.slug, "real-estate")

    def test_site_settings_refuses_a_second_row(self):
        from django.core.exceptions import ValidationError

        SiteSettings.objects.create(description="first")
        with self.assertRaises(ValidationError):
            SiteSettings(description="second").clean()

    def test_social_platform_is_unique(self):
        from django.db.utils import IntegrityError

        SocialLink.objects.create(platform="facebook", label="Facebook")
        with self.assertRaises(IntegrityError):
            SocialLink.objects.create(platform="facebook", label="Facebook again")


class SeedCommandTests(TestCase):
    def test_seed_is_idempotent(self):
        from django.core.management import call_command

        call_command("seed_content", verbosity=0)
        first = Industry.objects.count()
        call_command("seed_content", verbosity=0)

        self.assertEqual(Industry.objects.count(), first)
        self.assertEqual(first, 8)
        self.assertEqual(Package.objects.count(), 4)
        self.assertEqual(FaqItem.objects.count(), 7)
        self.assertEqual(TeamMember.objects.count(), 3)

    def test_seed_keeps_what_was_edited_in_the_admin(self):
        """Render re-seeds on every deploy, so edits have to survive it."""
        from django.core.management import call_command

        call_command("seed_content", verbosity=0)
        link = SocialLink.objects.get(platform="whatsapp")
        link.href = "https://wa.me/9779800000000"
        link.label = "Chat on WhatsApp"
        link.order = 9
        link.save()
        industry = Industry.objects.first()
        industry.pitch = "Rewritten by hand in the admin."
        industry.save()

        call_command("seed_content", verbosity=0)

        link.refresh_from_db()
        industry.refresh_from_db()
        self.assertEqual(link.href, "https://wa.me/9779800000000")
        self.assertEqual(link.label, "Chat on WhatsApp")
        self.assertEqual(link.order, 9)
        self.assertEqual(industry.pitch, "Rewritten by hand in the admin.")

    def test_seed_refills_a_field_left_blank(self):
        from django.core.management import call_command

        call_command("seed_content", verbosity=0)
        industry = Industry.objects.first()
        industry.pitch = ""
        industry.save()

        call_command("seed_content", verbosity=0)

        industry.refresh_from_db()
        self.assertNotEqual(industry.pitch, "")

    def test_seed_removes_a_platform_no_longer_offered(self):
        from django.core.management import call_command

        SocialLink.objects.create(platform="twitter", label="Twitter", order=7)

        call_command("seed_content", verbosity=0)

        self.assertFalse(SocialLink.objects.filter(platform="twitter").exists())
        self.assertEqual(
            sorted(SocialLink.objects.values_list("platform", flat=True)),
            ["facebook", "instagram", "linkedin", "whatsapp"],
        )

    def test_seed_keeps_a_dropped_platform_that_has_a_url(self):
        """Deleting a link someone filled in would be losing their work."""
        from django.core.management import call_command

        SocialLink.objects.create(platform="medium", label="Medium", href="https://medium.com/@orik")

        call_command("seed_content", verbosity=0)

        self.assertTrue(SocialLink.objects.filter(platform="medium").exists())


class AdminIconTests(TestCase):
    def test_every_platform_has_a_glyph(self):
        from content.icons import PLATFORM_PATHS

        for key, _ in SocialLink.PLATFORMS:
            self.assertIn(key, PLATFORM_PATHS, f"{key} would show a dash in the admin")

    def test_an_unknown_platform_falls_back_to_a_dash(self):
        from content.icons import glyph

        self.assertNotIn("<svg", glyph("myspace"))

    def test_the_changelist_draws_the_icons(self):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_superuser("iconadmin", "icon@example.com", "pw-for-tests")
        self.client.login(username="iconadmin", password="pw-for-tests")
        SocialLink.objects.create(platform="whatsapp", label="WhatsApp", href="https://wa.me/1")
        SocialLink.objects.create(platform="linkedin", label="LinkedIn")

        html = self.client.get("/admin/content/sociallink/").content.decode()

        self.assertEqual(html.count("<svg"), 2)
        # The one with no URL is dimmed, because the site hides it.
        self.assertIn("opacity:0.3", html)
        self.assertIn("opacity:1", html)

    def test_the_changelist_says_why_a_link_is_hidden(self):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_superuser("whyadmin", "why@example.com", "pw-for-tests")
        self.client.login(username="whyadmin", password="pw-for-tests")
        SocialLink.objects.create(platform="whatsapp", label="WhatsApp", href="https://wa.me/1")
        SocialLink.objects.create(platform="instagram", label="Instagram")
        SocialLink.objects.create(platform="facebook", label="Facebook", href="https://fb.com/x", is_published=False)

        html = self.client.get("/admin/content/sociallink/").content.decode()

        self.assertIn("add a URL", html)
        self.assertIn("unpublished", html)
        self.assertEqual(html.count(">Yes</b>"), 1)


class YourIdeaHighlightTests(TestCase):
    def test_the_api_carries_the_highlight_and_each_card_icon(self):
        from content.models import Problem, YourIdeaSection

        section = YourIdeaSection.objects.create(
            heading="Your business deserves more" + chr(10) + "than just a social media page.",
            heading_highlight="social media page.",
            closing_text="We turn those problems into something simple.",
        )
        Problem.objects.create(section=section, title="No website", description="x", icon="search-x", order=0)
        Problem.objects.create(section=section, title="Outdated website", description="y", icon="history", order=1)

        payload = self.client.get("/api/content/").json()

        self.assertEqual(payload["yourIdea"]["headingHighlight"], "social media page.")
        self.assertEqual([p["icon"] for p in payload["problems"]], ["search-x", "history"])

    def test_a_blank_highlight_is_allowed(self):
        """Leaving it empty means the heading is drawn without a marker."""
        from content.models import YourIdeaSection

        YourIdeaSection.objects.create(heading="Plain heading.", closing_text="z")

        payload = self.client.get("/api/content/").json()

        self.assertEqual(payload["yourIdea"]["headingHighlight"], "")


class FooterBottomTests(TestCase):
    def test_the_api_carries_the_wording_and_the_menu(self):
        from content.models import FooterBottomSection, FooterLink

        section = FooterBottomSection.objects.create(
            menu_label="Quick links",
            contact_label="Talk to us",
            enquiry_label="Start a project",
            enquiry_href="/contact",
            copyright_note="Built in Nepal.",
        )
        FooterLink.objects.create(section=section, label="Home", href="/", order=0)
        FooterLink.objects.create(section=section, label="Work", href="/work", order=1)

        footer = self.client.get("/api/content/").json()["footerBottom"]

        self.assertEqual(footer["menuLabel"], "Quick links")
        self.assertEqual(footer["contactLabel"], "Talk to us")
        self.assertEqual(footer["enquiryLabel"], "Start a project")
        self.assertEqual(footer["copyrightNote"], "Built in Nepal.")
        self.assertEqual([link["label"] for link in footer["menu"]], ["Home", "Work"])

    def test_an_unpublished_link_is_left_out(self):
        from content.models import FooterBottomSection, FooterLink

        section = FooterBottomSection.objects.create()
        FooterLink.objects.create(section=section, label="Home", href="/", order=0)
        FooterLink.objects.create(section=section, label="Draft", href="/draft", order=1, is_published=False)

        footer = self.client.get("/api/content/").json()["footerBottom"]

        self.assertEqual([link["label"] for link in footer["menu"]], ["Home"])

    def test_a_missing_section_still_answers(self):
        """The API must not 500 before the section has been created."""
        footer = self.client.get("/api/content/").json()["footerBottom"]

        self.assertEqual(footer["menuLabel"], "Menu")
        self.assertEqual(footer["menu"], [])


class WhatsAppNumberTests(TestCase):
    def test_a_number_writes_the_wa_me_link(self):
        link = SocialLink.objects.create(platform="whatsapp", label="WhatsApp", whatsapp_number="977 9800000000")

        link.refresh_from_db()

        self.assertEqual(link.href, "https://wa.me/9779800000000")

    def test_punctuation_in_the_number_is_dropped(self):
        link = SocialLink.objects.create(platform="whatsapp", label="WhatsApp", whatsapp_number="+977-980 000 0000")

        self.assertEqual(link.href, "https://wa.me/9779800000000")

    def test_other_platforms_keep_the_url_they_were_given(self):
        link = SocialLink.objects.create(
            platform="facebook", label="Facebook", whatsapp_number="977 1", href="https://facebook.com/orik"
        )

        self.assertEqual(link.href, "https://facebook.com/orik")

    def test_a_whatsapp_row_without_a_number_keeps_its_own_url(self):
        link = SocialLink.objects.create(platform="whatsapp", label="WhatsApp", href="https://wa.me/123")

        self.assertEqual(link.href, "https://wa.me/123")
