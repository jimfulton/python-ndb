import synthtool as s
from synthtool import gcp

AUTOSYNTH_MULTIPLE_PRS = True

common = gcp.CommonTemplates()

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(unit_cov_level=100, cov_level=100)
s.move(templated_files / '.kokoro')  # just move kokoro configs

s.replace([".kokoro/publish-docs.sh", ".kokoro/build.sh"], "cd github/python-ndb", 
"""cd github/python-ndb

# Need enchant for spell check
sudo apt-get update
sudo apt-get -y install dictionaries-common aspell aspell-en \\
                        hunspell-en-us libenchant1c2a enchant""")

s.replace(".kokoro/build.sh", """(export PROJECT_ID=.*)""", """\g<1>

if [[ -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]]; then
  # Configure local Redis to be used
  export REDIS_CACHE_URL=redis://localhost
  redis-server &

  # Configure local memcached to be used
  export MEMCACHED_HOSTS=127.0.0.1
  service memcached start

  # Install gcloud SDK
  mkdir -p /tmp/gcloud
  curl -sSL https://sdk.cloud.google.com | bash -s -- --install-dir=/tmp/gcloud
  export PATH=$PATH:/tmp/gcloud/google-cloud-sdk/bin

  # Some system tests require indexes. Use gcloud to create them.
  gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS --project=$PROJECT_ID
  gcloud --quiet --verbosity=debug datastore indexes create tests/system/index.yaml
fi
""")

s.replace(
    ".kokoro/docker/docs/Dockerfile",
    "libsqlite3-dev.*\n",
    "\g<0>    memcached \\\n"\
)

s.replace(
    ".kokoro/docker/docs/Dockerfile",
    "# Install dependencies.\n",
    """\g<0># Spell check related
RUN apt-get update && apt-get install -y dictionaries-common aspell aspell-en \\
  hunspell-en-us libenchant1c2a enchant
"""
)

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
