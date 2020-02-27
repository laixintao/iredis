# This file defines how PyOxidizer application building and packaging is
# performed. See the pyoxidizer crate's documentation for extensive
# documentation on this file format.

# Obtain the default PythonDistribution for our build target. We link
# this distribution into our produced executable and extract the Python
# standard library from it.
def make_dist():
    return default_python_distribution()

# Configuration files consist of functions which define build "targets."
# This function creates a Python executable and installs it in a destination
# directory.
def make_exe(dist):
    # This variable defines the configuration of the
    # embedded Python interpreter.
    python_config = PythonInterpreterConfig(
        run_eval="from iredis.entry import main; main()",
        # Allows the executable to load deps from this folder
        sys_paths=["$ORIGIN/lib"]
    )

    # Produce a PythonExecutable from a Python distribution, embedded
    # resources, and other options. The returned object represents the
    # standalone executable that will be built.
    exe = dist.to_python_executable(
        name="iredis",
        config=python_config,
        # Embed all extension modules, making this a fully-featured Python.
        extension_module_filter='all',

        # Only package the minimal set of extension modules needed to initialize
        # a Python interpreter. Many common packages in Python's standard
        # library won't work with this setting.
        #extension_module_filter='minimal',

        # Only package extension modules that don't require linking against
        # non-Python libraries. e.g. will exclude support for OpenSSL, SQLite3,
        # other features that require external libraries.
        #extension_module_filter='no-libraries',

        # Only package extension modules that don't link against GPL licensed
        # libraries.
        #extension_module_filter='no-gpl',

        # Include Python module sources. This isn't strictly required and it does
        # make binary sizes larger. But having the sources can be useful for
        # activities such as debugging.
        include_sources=True,

        # Whether to include non-module resource data/files.
        include_resources=False,

        # Do not include functionality for testing Python itself.
        include_test=False,
    )

    # Discover Python files from a virtualenv and add them to our embedded
    # context.
    #exe.add_python_resources(dist.read_virtualenv(path="/path/to/venv"))

    # Filter all resources collected so far through a filter of names
    # in a file.
    #exe.filter_from_files(files=["/path/to/filter-file"]))

    # Return our `PythonExecutable` instance so it can be built and
    # referenced by other consumers of this target.
    return exe

def make_embedded_data(exe):
    return exe.to_embedded_data()

def make_install(dist, exe):
    # Create an object that represents our installed application file layout.
    files = FileManifest()

    # Add the generated executable to our install layout in the root directory.
    files.add_python_resource(".", exe)

    # Include pip dependencies alongside the executable
    # WHEEL_PATH will be replaced with envsubst because pyoxidizer doesn't support env vars
    files.add_python_resources("lib", dist.pip_install(["$WHEEL_PATH"]))

    return files

# Tell PyOxidizer about the build targets defined above.
register_target("dist", make_dist)
register_target("exe", make_exe, depends=["dist"], default=True)
register_target("embedded", make_embedded_data, depends=["exe"], default_build_script=True)
register_target("install", make_install, depends=["dist", "exe"])

# Resolve whatever targets the invoker of this configuration file is requesting
# be resolved.
resolve_targets()

# END OF COMMON USER-ADJUSTED SETTINGS.
#
# Everything below this is typically managed by PyOxidizer and doesn't need
# to be updated by people.

PYOXIDIZER_VERSION = "0.6.0"
PYOXIDIZER_COMMIT = ""
