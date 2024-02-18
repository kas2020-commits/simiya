{
  description = "Simiya";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, flake-utils, ... }:
    let
      repo = import ./nix;
      versions = repo.versions;
    in
    flake-utils.lib.eachSystem versions.supportedSystems
      (system:
        let
          pkgs = import nixpkgs { inherit system; };
          shells = repo.devShell { inherit pkgs versions; };
        in
        {
          formatter = pkgs.nixpkgs-fmt;
          devShells = {
            nopylibs = shells.nopylibs;
            pylibs = shells.pylibs;
            default = shells.pylibs;
          };
          packages = {
            default = repo.compiler {
              inherit pkgs versions;
              src = ./.;
            };
          };
        }
      );
}
