#
# Copyright (C) 2018 CZ.NIC z.s.p.o. (http://www.nic.cz/)
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=vcversioner
PKG_VERSION:=2.16
PKG_RELEASE:=1
PKG_SOURCE_SUBDIR:=$(PKG_NAME)
#PKG_SOURCE_PROTO:=git
#PKG_SOURCE_URL:=https://gitlab.labs.nic.cz/turris/foris-schema
#PKG_SOURCE_VERSION:=v$(PKG_VERSION)
#PKG_SOURCE:=$(PKG_NAME)-$(PKG_SOURCE_VERSION).tar.gz
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)
PKG_HOST_BUILD_DIR:=$(BUILD_DIR_HOST)/$(PKG_NAME)-$(PKG_VERSION)
PKG_LICENSE:=GPL-3.0

include $(INCLUDE_DIR)/host-build.mk
include $(INCLUDE_DIR)/package.mk
$(call include_mk, python-package.mk)
$(call include_mk, python-host.mk)

define Package/$(PKG_NAME)
	TITLE:=python-vcversioner
    DEPENDS:=+python
	CATEGORY:=ZL100MT
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) ./src/* $(PKG_BUILD_DIR)/
endef

define Package/$(PKG_NAME)/description
	Library which validates whether the json matches
	the protocol use between Foris web and a configuration backend.
endef

define Build/Compile
	#$(call Build/Compile/PyMod,,install --prefix="/usr" --root="$(STAGING_DIR)")
	$(call Build/Compile/PyMod,,install --prefix="/usr" --root="$(PKG_INSTALL_DIR)")
endef

#define Package/$(PKG_NAME)/conffiles
#endef

define Package/$(PKG_NAME)/install
	#$(INSTALL_DIR) $(1)$(PYTHON_PKG_DIR)/
	@echo "xijia PYTHON_PKG_DIR $(PYTHON_PKG_DIR)"
	@echo "xijia INSTALL_DIR $(INSTALL_DIR)"
	@echo "xijia 1111 $(1)"
	@echo "xijia PKG_INSTALL_DIR $(PKG_INSTALL_DIR)"
	$(INSTALL_DIR) $(1)
	$(CP) \
		$(PKG_INSTALL_DIR)$(PYTHON_PKG_DIR)/* \
		$(1)$(PYTHON_PKG_DIR)/usr/lib/python2.7/site-packages/
endef

define Host/Prepare
	mkdir -p $(BUILD_DIR_HOST)/$(PKG_NAME)-$(PKG_VERSION)
	$(CP) ./src/* $(BUILD_DIR_HOST)/$(PKG_NAME)-$(PKG_VERSION)
endef

define Host/Compile
	$(call Build/Compile/HostPyMod,,build)
endef

define Host/Install
	$(call Build/Compile/HostPyMod,,install --prefix="" --root="$(STAGING_DIR)/host")
endef

$(eval $(call HostBuild))

$(eval $(call PyPackage,$(PKG_NAME)))
$(eval $(call BuildPackage,$(PKG_NAME)))
