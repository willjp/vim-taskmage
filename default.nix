# Defines minimal env to run code/tests within interpreter.
# (optionally, override with your preferred packages in with a `shell.nix`)
#
# If you just want to run tests, use `python setup.py test`.
# See https://nixos.org/features.html
#
# Run:
#    nix-shell

{ 
  pkgs ? import <nixpkgs> {}, 
  mach-nix ? import (builtins.fetchGit { url = "https://github.com/DavHau/mach-nix/"; ref = "refs/tags/3.1.1"; }) { python = "python38"; },
  extra_python_requirements ? []
}:

let
  python_requirements = 
    pkgs.lib.strings.splitString "\n" (builtins.readFile ./tests/requirements.txt)
    ++ extra_python_requirements;

  python = (mach-nix.mkPython {
    requirements = (pkgs.lib.strings.concatStrings (map(x: "${x}\n") python_requirements));
  });

in
  pkgs.stdenv.mkDerivation {
    name = "nixpython-1.0.0";
    buildInputs = [
      pkgs.hello
      python
    ];
    shellHook = ''
      export PYTHONPATH+=":$(pwd)/plugin"
    '';
  }

