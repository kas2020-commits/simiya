{
  description = "Turnstone Monorepo - The one-stop-shop for all platform development";

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
          backend = repo.targets.backend {
            inherit pkgs versions;
            src = ./backend/python;
          };
          backend_container = tur: tag: repo.containers.backend {
            inherit pkgs versions tur tag;
          };
          shells = repo.devShell { inherit pkgs versions; };
        in
        {
          formatter = pkgs.nixpkgs-fmt;
          devShells = {
            nopylibs = shells.nopylibs;
            pylibs = shells.pylibs;
            default = shells.nopylibs;
          };
          packages = {
            backend = {
              l0 = backend.l0;
              l1 = backend.l1;
              l2 = backend.l2;
            };
            container = {
              backend = {
                l0 = backend_container backend.l0 "l0";
                l1 = backend_container backend.l1 "l1";
                l2 = backend_container backend.l2 "l2";
              };
            };
            default = backend.l2;
          };
        }
      );
}
