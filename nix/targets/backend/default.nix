{ pkgs, versions, src }:
let
  pyPackages = pkgs."${versions.python}Packages";
  deps = import ./deps { inherit pkgs versions; };
in
{
  # mkBackend = depsLayer: pyPackages.buildPythonApplication {
  mkBackend = pyPackages.buildPythonPackage {
    pname = "tur";
    nativeBuildInputs = deps.native;
    propagatedBuildInputs = deps.propagate;
    version = versions.backend;
    src = src;
    pyproject = true;
  };
}

