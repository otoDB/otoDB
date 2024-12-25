{
  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixos-unstable";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
  };
  outputs = { nixpkgs, flake-utils, ... }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree= true;
      };
      django_bitfield = let
          pname = "django-bitfield";
          version = "2.2.0";
        in
        pkgs.python3Packages.buildPythonPackage {
          inherit pname version;
          src = pkgs.fetchPypi {
            inherit pname version;
            sha256 = "sha256-GyEmKsxOwK8/gu0ESYoFbNnVRSUyrAJ3HgBINaNOCxs=";
          };
        };
    in rec {
      devShell = pkgs.mkShell {
        buildInputs = with pkgs; [
          (python312.withPackages (pp: [
            pp.six
            pp.diff-match-patch
            pp.django
            django_bitfield
            pp.django-simple-history
            pp.django_taggit
            pp.dotmap
            pp.python-dotenv
            pp.pyyaml
            pp.yt-dlp
          ]))
        ];
      };
    }
  );
}
