{ pkgs, versions, src }:
let
  pyPackages = pkgs."${versions.python}Packages";
  deps = import ./deps { inherit pkgs versions; };
in
pyPackages.buildPythonPackage {
  pname = "simiya";
  nativeBuildInputs = deps.native;
  propagatedBuildInputs = deps.propagate;
  version = versions.backend;
  src = src;
  pyproject = true;
}

