#
# Copyright (C) 2009-2010 Jo-Philipp Wich <xm@subsignal.org>
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=zl100mt-app
PKG_RELEASE:=1.0.0

PKG_BUILD_DIR := $(BUILD_DIR)/$(PKG_NAME)

include $(INCLUDE_DIR)/package.mk

define Package/$(PKG_NAME)
  SECTION:=utils
  CATEGORY:=Base system
  TITLE:=daemon application for zl100mt, including relay BeiDou data, etc.
  DEPENDS:=+libftdi +libblobmsg-json +libubox +libjson-c +libubus
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
	echo $(PKG_RELEASE) > $(1)/etc/zl100mt-version
	$(INSTALL_DATA) ./files/etc/zl100mt-app/zl100mt-app.conf $(1)/etc/zl100mt-app/
	$(INSTALL_DIR) $(1)/etc/config
	$(INSTALL_DATA) ./files/etc/zl100mt-app/rtmp.conf $(1)/etc/config/rtmp
	$(INSTALL_DIR) $(1)/usr/sbin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/$(PKG_NAME) $(1)/usr/sbin/
	$(INSTALL_BIN) ./files/zl100mt-poller $(1)/usr/sbin/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/ft4232_bitbang $(1)/usr/sbin/

	$(INSTALL_DIR) $(1)/etc/cron.d
	$(INSTALL_DATA) ./files/zl100mt-cron $(1)/etc/cron.d/zl100mt
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/etc/zl100mt-app/zl100mt-app.init $(1)/etc/init.d/zl100mt-app
	$(INSTALL_DIR) $(1)/etc/syslog-ng.d
	$(INSTALL_DATA) ./files/syslog-ng.conf $(1)/etc/syslog-ng.d/zl100mt
	$(INSTALL_DIR) $(1)/etc/logrotate.d
	$(INSTALL_DATA) ./files/logrotate.conf $(1)/etc/logrotate.d/zl100mt
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) ./files/zl100mt-temperature.sh $(1)/usr/bin/zl100mt-temperature.sh
	$(INSTALL_BIN) ./files/zl100mt-ntpdate.sh $(1)/usr/bin/zl100mt-ntpdate.sh
	$(INSTALL_BIN) ./files/check_default_route.sh $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/etc/hotplug.d/iface
	$(INSTALL_BIN) ./files/99-zl100mt-wanstate $(1)/etc/hotplug.d/iface/
	$(INSTALL_DIR) $(1)/usr/libexec/rpcd
	$(INSTALL_BIN) ./files/zl100mt-rpcd $(1)/usr/libexec/rpcd/zl100mt-rpcd
	$(INSTALL_DIR) $(1)/lib/netifd/proto
	$(INSTALL_BIN) ./files/inno_cdc.sh $(1)/lib/netifd/proto/inno_cdc.sh
	$(INSTALL_DIR) $(1)/etc/gcom/
	$(INSTALL_BIN) ./files/zl100mt-4g.gcom $(1)/etc/gcom/zl100mt-4g.gcom
	$(INSTALL_BIN) ./files/zl100mt-zw.gcom $(1)/etc/gcom/zl100mt-zw.gcom
	$(INSTALL_DATA) ./files/inno_cdc.json $(1)/etc/gcom/inno_cdc.json
	$(INSTALL_DIR) $(1)/root
	$(INSTALL_DATA) ./files/.vimrc $(1)/root
endef

$(eval $(call BuildPackage,$(PKG_NAME)))
