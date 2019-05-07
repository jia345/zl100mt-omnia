#
# Copyright (C) 2009-2010 Jo-Philipp Wich <xm@subsignal.org>
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=zl100mt-app
PKG_RELEASE:=1

PKG_BUILD_DIR := $(BUILD_DIR)/$(PKG_NAME)

include $(INCLUDE_DIR)/package.mk

define Package/$(PKG_NAME)
  SECTION:=utils
  CATEGORY:=Base system
  TITLE:=daemon application for zl100mt, including relay BeiDou data, etc.
  DEPENDS:=+libftdi
endef

define Package/$(PKG_NAME)/description
 This package contains main applicaton for zl100mt
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) ./src/* $(PKG_BUILD_DIR)/
endef

define Build/Configure
endef

define Build/Compile
	@echo Compiling zl100mt-app......
	$(MAKE) all -C $(PKG_BUILD_DIR) \
		CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)"
endef

define Package/$(PKG_NAME)/conffiles
/etc/zl100mt-app/zl100mt-app.conf
endef

define Package/$(PKG_NAME)/install
	@echo Installing zl100mt-app......
	$(INSTALL_DIR) $(1)/etc/zl100mt-app
	$(INSTALL_DATA) ./files/etc/zl100mt-app/zl100mt-app.conf $(1)/etc/zl100mt-app/
	$(INSTALL_DIR) $(1)/usr/sbin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/$(PKG_NAME) $(1)/usr/sbin/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/ft4232_bitbang $(1)/usr/sbin/

	$(INSTALL_DIR) $(1)/etc/cron.d
	$(INSTALL_DATA) ./files/cron.conf $(1)/etc/cron.d/zl100mt
	$(INSTALL_DIR) $(1)/etc/syslog-ng.d
	$(INSTALL_DATA) ./files/syslog-ng.conf $(1)/etc/syslog-ng.d/zl100mt
	$(INSTALL_DIR) $(1)/etc/logrotate.d
	$(INSTALL_DATA) ./files/logrotate.conf $(1)/etc/logrotate.d/zl100mt
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) ./files/temperature.sh $(1)/usr/bin/temperature.sh
endef

$(eval $(call BuildPackage,$(PKG_NAME)))
