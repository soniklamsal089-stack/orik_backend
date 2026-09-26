from whitenoise.storage import CompressedManifestStaticFilesStorage


class ForgivingManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """Fingerprinted static files that tolerate a missing manifest entry.

    Jazzmin's dashboard template resolves `vendor/bootswatch`, a directory
    rather than a file, so it never lands in the manifest. The strict default
    raises ValueError there, which turns the admin into a 500 the moment you
    log in. Falling back to the unhashed path keeps long-term caching for every
    asset that *is* in the manifest, and degrades gracefully for the ones that
    are not.
    """

    manifest_strict = False
