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
      django-bitfield = let
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
      django-tagulous = let
          pname = "django_tagulous"; # WTF, the package name is a hyphen but the DL is underscore
          version = "2.1.0";
        in
        pkgs.python3Packages.buildPythonPackage {
          inherit pname version;
          pyproject = true;
          build-system = [ pkgs.python3Packages.setuptools ];
          dependencies = with pkgs.python3Packages; [ django setuptools ];
          src = pkgs.fetchPypi {
            inherit pname version;
            sha256 = "sha256-9im1StcgBSCSeFsNzgVtxqaMe2P4EmB1r5wlhIslC/0=";
          };
        };
      django-wiki = let
          pname = "wiki"; # WTF, the package name is a hyphen but the DL is underscore
          version = "0.11.2";
        in
        pkgs.python3Packages.buildPythonPackage {
          inherit pname version;
          pyproject = true;
          build-system = [ pkgs.python3Packages.hatchling ];
          dependencies = with pkgs.python3Packages; [ django hatchling hatch-build-scripts ];
          src = pkgs.fetchPypi {
            inherit pname version;
            sha256 = "sha256-acw0j/fDw5NtZqK9R6ayhsLnXvBBQLTJxkSXc2wVlNc=";
          };
        };
    in rec {
      devShell = pkgs.mkShell {
        buildInputs = with pkgs; [
          (python312.withPackages (pp: [
            pp.six
            pp.diff-match-patch
            pp.django
            django-bitfield
            pp.django-simple-history
            pp.dotmap
            pp.python-dotenv
            pp.pyyaml
            # NEW
            django-tagulous
            pp.yt-dlp
            pp.django-model-utils
            pp.pypinyin
            pp.pykakasi
            django-wiki
            pp.pillow
            pp.django-mptt
            pp.django-sekizai
            pp.sorl-thumbnail
            pp.markdown
            pp.pymdown-extensions
          ]))
        ];
      };
    }
  );
}
