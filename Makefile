SHELL := /bin/bash
INSTALL_SH := linux/install.sh

.PHONY: help prepare check install update uninstall load

help:
	@echo ""
	@echo "German (US Mix) Keyboard Layout – Linux Installer"
	@echo "=================================================="
	@echo ""
	@echo "  make prepare    Check dependencies and install missing ones"
	@echo "  make check      Show installation status"
	@echo "  make install    Install layout system-wide  (requires sudo)"
	@echo "  make update     Update the symbol file only (requires sudo)"
	@echo "  make uninstall  Remove the layout           (requires sudo)"
	@echo "  make load       Temporarily load for this session (no sudo)"
	@echo ""
	@echo "Typical workflow:"
	@echo "  make prepare && make check && sudo make install"
	@echo ""

prepare:
	@bash $(INSTALL_SH) prepare

check:
	@bash $(INSTALL_SH) check

install:
	@bash $(INSTALL_SH) install

update:
	@bash $(INSTALL_SH) update

uninstall:
	@bash $(INSTALL_SH) uninstall

load:
	@bash $(INSTALL_SH) load
