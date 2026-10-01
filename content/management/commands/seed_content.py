"""Load the site's current copy into the database.

The text here is a straight port of frontend/src/data/home.ts and site.ts as of
the migration to a database-backed frontend. Safe to re-run: it updates rows in
place and never duplicates them.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import (
    DigitalExperiencesSection,
    FooterBottomSection,
    FooterLink,
    FooterTopSection,
    IndustriesSection,
    Template,
    FaqItem,
    HeroBadge,
    HeroSection,
    Industry,
    Package,
    Problem,
    ProcessStep,
    Project,
    SiteSettings,
    SocialLink,
    Stat,
    TeamMember,
    Testimonial,
    YourIdeaSection,
)

YOUR_IDEA = {
    "heading": "Your business deserves more\nthan just a social media page.",
    "closing_text": (
        "We turn those problems into a simple digital experience that helps customers discover, understand "
        "and contact your business."
    ),
    "heading_highlight": "social media page.",
    "cta_label": "Get a free consultation",
    "cta_href": "/contact",
}

SITE = {
    "name": "ORIK Webcraft",
    "description": (
        "ORIK Webcraft builds modern websites, landing pages, chatbots and digital solutions that help "
        "businesses build credibility, reach customers and generate enquiries."
    ),
}

HERO = {
    "heading": "Website design that works for your business.",
    "subheading": (
        "Modern websites, landing pages, chatbots and digital solutions designed to help businesses build "
        "credibility, reach customers and generate enquiries."
    ),
    "qualities_label": "Every ORIK website is:",
    "qualities": "Mobile\nFast\nModern",
}

# Order matters: the frontend positions badge 1-4 around the image.
HERO_BADGES = [
    ("More enquiries", "enquiries"),
    ("WhatsApp ready", "whatsapp"),
    ("Mobile ready", "mobile"),
    ("SEO ready", "seo"),
]

# The four the footer is meant to show. Each starts with an empty href, so
# nothing appears on the site until a real profile URL is filled in.
SOCIALS = [
    ("whatsapp", "WhatsApp"),
    ("instagram", "Instagram"),
    ("facebook", "Facebook"),
    ("linkedin", "LinkedIn"),
]

FOOTER_BOTTOM = {
    "menu_label": "Menu",
    "contact_label": "Contact Us",
    "enquiry_label": "Send us an enquiry",
    "enquiry_href": "/contact",
    "copyright_note": "All Rights Reserved.",
}

FOOTER_LINKS = [
    ("Home", "/"),
    ("Work", "/work"),
    ("About", "/about"),
    ("Process", "/process"),
    ("Pricing", "/pricing"),
    ("FAQ", "/faq"),
    ("Contact", "/contact"),
]

DIGITAL_EXPERIENCES = {
    "heading": "Digital experiences built\nfor modern business.",
    "link_label": "Get a free consultation",
    "link_href": "/contact",
}

STATS = [
    ("10+", "projects and concepts"),
    ("5+", "industries served"),
    ("100%", "responsive websites"),
    ("24/7", "online presence for your business"),
    ("5+", "demo projects to explore"),
    ("6", "digital services under one roof"),
]

PROBLEMS = [
    (
        "No website",
        "Customers search online first. Without a website they can't find you, so they find a competitor instead.",
        "search-x",
    ),
    (
        "Outdated website",
        "A slow or old-looking site makes a great business look unreliable, especially on a phone.",
        "history",
    ),
    (
        "Difficult to contact",
        "If people can't quickly call, message or send an enquiry, they leave before they ever reach you.",
        "message-circle-off",
    ),
]

TEMPLATES = [
    ("restaurant", "Saffron Table", "saffrontable.demo", "Fresh flavours, served daily",
     "Book a table or order online in seconds.", "Book a table",
     ["Menu", "Book", "Contact"], ["Breakfast", "Lunch", "Dinner"]),
    ("corporate", "Summit Group", "summitgroup.demo", "Business solutions that scale",
     "Consulting and services for growing companies.", "Talk to us",
     ["About", "Services", "Careers"], ["Strategy", "Operations", "Support"]),
    ("education", "BrightPath Education", "brightpath.demo", "Study abroad with confidence",
     "Guidance for courses, visas and applications.", "Book a consultation",
     ["Courses", "Countries", "Contact"], ["Australia", "UK", "Canada"]),
    ("travel", "Horizon Trails", "horizontrails.demo", "Plan your next adventure",
     "Guided tours, treks and holidays made simple.", "Explore tours",
     ["Tours", "Destinations", "Contact"], ["Trekking", "City tours", "Adventure"]),
    ("retail", "Urban Thread", "urbanthread.demo", "New season, new styles",
     "Shop the latest collection online.", "Shop now",
     ["Women", "Men", "Sale"], ["Jackets", "Dresses", "Sneakers"]),
    ("realEstate", "Keystone Realty", "keystonerealty.demo", "Find the home that fits your life",
     "Apartments, houses and land in great locations.", "View listings",
     ["Buy", "Rent", "Agents"], ["Apartments", "Houses", "Land"]),
    ("professional", "Clarity Advisors", "clarityadvisors.demo", "Expert advice you can rely on",
     "Accounting, tax and legal support for small businesses.", "Schedule a call",
     ["Services", "Team", "Insights"], ["Accounting", "Tax", "Legal"]),
    ("local", "Corner Bakery", "cornerbakery.demo", "Baked fresh every morning",
     "Cakes, breads and coffee just around the corner.", "Order now",
     ["Menu", "Offers", "Visit"], ["Cakes", "Breads", "Coffee"]),
]

INDUSTRIES = [
    (
        "Restaurants & Cafes",
        "Show your menu, take bookings and get found by hungry customers nearby.",
        ["Digital menu with photos", "Table booking and WhatsApp orders", "Google Maps and opening hours"],
        "restaurant",
    ),
    (
        "Corporate Businesses",
        "A credible website that builds trust with clients and partners.",
        ["Company profile and service pages", "Team and leadership sections", "Enquiry forms that reach the right people"],
        "corporate",
    ),
    (
        "Education & Consultancies",
        "Help students understand your programs and book consultations with confidence.",
        ["Course and destination pages", "Consultation booking form", "Success stories and FAQs"],
        "education",
    ),
    (
        "Travel & Tourism",
        "Inspire travellers with beautiful tour pages and effortless enquiries.",
        ["Tour packages with itineraries", "Enquiry and booking forms", "Photo galleries and reviews"],
        "travel",
    ),
    (
        "Retail & E-commerce",
        "Sell online with a store that works beautifully on every phone.",
        ["Product catalogue and categories", "Cart and mobile checkout", "Offers and new arrivals"],
        "retail",
    ),
    (
        "Real Estate",
        "Showcase listings with rich photos and let buyers contact agents instantly.",
        ["Property listings with filters", "Photo galleries and floor plans", "Agent contact and site-visit requests"],
        "realEstate",
    ),
    (
        "Professional Services",
        "Build authority and let clients book a call without back-and-forth.",
        ["Service and expertise pages", "Case studies and credentials", "Consultation booking"],
        "professional",
    ),
    (
        "Local Business",
        "Get found by people nearby and turn searches into walk-ins and calls.",
        ["Google Maps and directions", "Opening hours and offers", "Click-to-call and WhatsApp"],
        "local",
    ),
]

PROJECTS = [
    (
        "Urban Thread",
        "E-commerce website",
        "An online clothing store concept with product categories, a cart and a mobile-first checkout.",
        ["Product catalogue", "Cart and checkout", "Mobile-first design"],
        "retail",
    ),
    (
        "BrightPath Education",
        "Education / Consultancy",
        "A consultancy website that guides students through courses and destinations and turns visits into consultations.",
        ["Course pages", "Consultation form", "FAQ section"],
        "education",
    ),
    (
        "Summit Group",
        "Corporate website",
        "A credible corporate website presenting services, team and expertise with clear enquiry paths.",
        ["Service pages", "Team profiles", "Lead capture"],
        "corporate",
    ),
]

PROCESS_STEPS = [
    ("Discover", "We learn about your business, customers and goals in a free consultation."),
    ("Plan", "We map out pages, content and features, and agree on scope and timeline."),
    ("Design", "We design a modern look for your brand and refine it with your feedback."),
    ("Develop", "We build a fast, responsive website with forms, WhatsApp and the features you need."),
    ("Launch", "We test everything, connect your domain and take your website live."),
    ("Support", "We stay available for updates, fixes and improvements as your business grows."),
]

PACKAGES = [
    ("Starter", "For businesses getting online for the first time.", ["1-page business website", "Mobile-friendly design", "Contact section"]),
    ("Business", "For a complete, professional online presence.", ["4–6 page professional website", "Mobile-friendly design", "Contact form"]),
    ("Growth", "For businesses ready to turn visitors into enquiries.", ["Professional website", "WhatsApp integration", "Enquiry forms", "Basic SEO setup"]),
    ("Custom", "For businesses with special requirements.", ["Custom website", "Chatbot integration", "Special functionality"]),
]

TEAM = [
    ("Rohan Shah", "Founder & CEO", "rohan@orikwebcraft.com", "+977-9801234567", "https://www.linkedin.com/in/rohan-shah", "https://www.facebook.com/rohan.shah", "https://www.instagram.com/rohan_shah", "https://res.cloudinary.com/dr54mqokd/image/upload/v1/team/member-one.png"),
    ("Sonik Lamsal", "Co-Founder & CTO", "sonik@orikwebcraft.com", "+977-9812345678", "https://www.linkedin.com/in/sonik-lamsal", "https://www.facebook.com/sonik.lamsal", "https://www.instagram.com/sonik_lamsal", "https://res.cloudinary.com/dr54mqokd/image/upload/v1/team/member-two.jpg"),
    ("Subham Karki", "Lead Designer", "subham@orikwebcraft.com", "+977-9823456789", "https://www.linkedin.com/in/subham-karki", "https://www.facebook.com/subham.karki", "https://www.instagram.com/subham_karki", "https://res.cloudinary.com/dr54mqokd/image/upload/v1/team/member-three.jpg"),
]

FAQS = [
    (
        "How long does it take to build a website?",
        "It depends on the package and how quickly your content is ready. A one-page website is faster than a "
        "multi-page site, and we'll give you a clear timeline after the free consultation.",
    ),
    (
        "How much does a website cost?",
        "Every business has different needs, so we quote each project after understanding your goals. Choose a "
        "package and request a quote. The consultation is free.",
    ),
    (
        "Will my website work on mobile phones?",
        "Yes. Every website we build is responsive, so it looks and works great on phones, tablets and desktops.",
    ),
    (
        "Can you add WhatsApp and a chatbot?",
        "Yes. We can add WhatsApp click-to-chat buttons, enquiry flows and website chatbots so customers can reach "
        "you faster.",
    ),
    (
        "Do you help with SEO?",
        "Our Growth package includes a basic SEO setup, so search engines can understand your pages and customers "
        "can find you more easily.",
    ),
    (
        "What happens after my website goes live?",
        "We offer website maintenance and personal support for updates, fixes and content changes whenever you "
        "need them.",
    ),
    (
        "What do I need to get started?",
        "Just a short conversation about your business. If you have a logo, photos or text, great. If not, we'll "
        "guide you through what's needed.",
    ),
]


class Command(BaseCommand):
    help = "Populate the database with the site's current copy. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing content rows first, discarding any admin edits.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.quiet = options["verbosity"] == 0
        if options["reset"]:
            for model in (HeroBadge, Template, SocialLink, FooterLink, Stat, Problem, Industry, Project, ProcessStep, Package, TeamMember, Testimonial, FaqItem):
                model.objects.all().delete()
            HeroSection.objects.all().delete()
            YourIdeaSection.objects.all().delete()
            DigitalExperiencesSection.objects.all().delete()
            IndustriesSection.objects.all().delete()
            FooterTopSection.objects.all().delete()
            FooterBottomSection.objects.all().delete()
            self.say(self.style.WARNING("Existing content deleted."))

        settings_row, _ = SiteSettings.objects.get_or_create(pk=1, defaults=SITE)
        if not settings_row.description:
            settings_row.description = SITE["description"]
            settings_row.save()

        # Only fills a hero that doesn't exist yet, so re-running never
        # overwrites wording edited in the admin.
        hero, hero_created = HeroSection.objects.get_or_create(pk=1, defaults=HERO)
        self.say(f"  hero: {'created' if hero_created else 'left as edited'} ({hero.heading[:40]})")

        footer_bottom, _ = FooterBottomSection.objects.get_or_create(pk=1, defaults=FOOTER_BOTTOM)
        idea, idea_created = YourIdeaSection.objects.get_or_create(pk=1, defaults=YOUR_IDEA)
        self.say(f"  your idea: {'created' if idea_created else 'left as edited'}")

        digital, digital_created = DigitalExperiencesSection.objects.get_or_create(pk=1, defaults=DIGITAL_EXPERIENCES)
        self.say(f"  digital experiences: {'created' if digital_created else 'left as edited'}")

        industries_section, industries_created = IndustriesSection.objects.get_or_create(pk=1)
        self.say(f"  industries section: {'created' if industries_created else 'left as edited'}")

        footer_top, footer_created = FooterTopSection.objects.get_or_create(pk=1)
        self.say(f"  footer top: {'created' if footer_created else 'left as edited'}")

        templates = {}
        created = updated = 0
        for index, (key, name, domain, headline, subline, cta, nav, cards) in enumerate(TEMPLATES):
            template, was_created = Template.objects.update_or_create(
                key=key,
                defaults={
                    "name": name, "domain": domain, "headline": headline, "subline": subline,
                    "cta": cta, "nav": "\n".join(nav), "cards": "\n".join(cards), "order": index,
                },
            )
            templates[key] = template
            created += was_created
            updated += not was_created
        self.say(f"  templates: {created} created, {updated} updated")

        counts = {
            "hero badges": self._seed(
                HeroBadge, HERO_BADGES, lambda i, row: ({"hero": hero, "label": row[0]}, {"icon": row[1], "order": i})
            ),
            "footer links": self._seed(
                FooterLink, FOOTER_LINKS, lambda i, row: ({"label": row[0]}, {"section": footer_bottom, "href": row[1], "order": i})
            ),
            "social links": self._seed(SocialLink, SOCIALS, lambda i, row: ({"platform": row[0]}, {"label": row[1], "order": i})),
            "stats": self._seed(
                Stat, STATS, lambda i, row: ({"value": row[0], "label": row[1]}, {"section": digital, "order": i})
            ),
            "problems": self._seed(
                Problem,
                PROBLEMS,
                lambda i, row: ({"title": row[0]}, {"section": idea, "description": row[1], "icon": row[2], "order": i}),
            ),
            "industries": self._seed(
                Industry,
                INDUSTRIES,
                lambda i, row: (
                    {"name": row[0]},
                    {"pitch": row[1], "features": "\n".join(row[2]), "template_industry": templates[row[3]], "order": i},
                ),
            ),
            "projects": self._seed(
                Project,
                PROJECTS,
                lambda i, row: (
                    {"title": row[0]},
                    {
                        "category": row[1],
                        "description": row[2],
                        "features": "\n".join(row[3]),
                        "template_project": templates[row[4]],
                        "order": i,
                    },
                ),
            ),
            "process steps": self._seed(ProcessStep, PROCESS_STEPS, lambda i, row: ({"title": row[0]}, {"description": row[1], "order": i})),
            "packages": self._seed(Package, PACKAGES, lambda i, row: ({"name": row[0]}, {"tagline": row[1], "features": "\n".join(row[2]), "order": i})),
            "team": self._seed(TeamMember, TEAM, lambda i, row: (
                {"name": row[0]}, 
                {
                    "role": row[1], 
                    "email": row[2], 
                    "whatsapp": row[3], 
                    "linkedin": row[4], 
                    "facebook": row[5], 
                    "instagram": row[6], 
                    "photo": row[7] if len(row) > 7 else "",
                    "order": i
                }
            )),
            "FAQs": self._seed(FaqItem, FAQS, lambda i, row: ({"question": row[0]}, {"answer": row[1], "order": i})),
        }

        for label, (created, updated) in counts.items():
            self.say(f"  {label}: {created} created, {updated} updated")

        # Platforms dropped from SOCIALS linger in databases seeded earlier.
        # Only the ones with no URL go: a filled-in link is content someone typed.
        stale = SocialLink.objects.exclude(platform__in=[key for key, _ in SOCIALS]).filter(href="")
        names = sorted(row.label or row.platform for row in stale)
        if names:
            stale.delete()
            self.say(self.style.WARNING(f"  removed unused social links: {', '.join(names)}"))
        self.say(self.style.SUCCESS("Content seeded. Testimonials are intentionally left empty; team rows are placeholders to edit."))

    def say(self, message):
        if not self.quiet:
            self.stdout.write(message)

    @staticmethod
    def _seed(model, rows, build):
        """Creates missing rows, and on rows that already exist fills only blanks.

        Content edited in the admin has to survive the next deploy, and Render
        runs this command on every one, so an existing value is never replaced.
        `order` is left alone entirely: reordering happens on the list page.
        """
        created = updated = 0
        for index, row in enumerate(rows):
            lookup, defaults = build(index, row)
            existing = model.objects.filter(**lookup).first()
            if existing is None:
                model.objects.create(**lookup, **defaults)
                created += 1
                continue
            gaps = {}
            for field, value in defaults.items():
                if field == "order":
                    continue
                # attname is "<field>_id" for a relation, so no extra query.
                if not getattr(existing, model._meta.get_field(field).attname):
                    gaps[field] = value
            if gaps:
                for field, value in gaps.items():
                    setattr(existing, field, value)
                existing.save(update_fields=list(gaps))
                updated += 1
        return created, updated