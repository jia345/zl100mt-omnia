/*
 * Copyright (C) 2015 Stefan Roese <sr@denx.de>
 *
 * SPDX-License-Identifier:	GPL-2.0+
 */

#include <common.h>
#include <i2c.h>
#include <miiphy.h>
#include <netdev.h>
#include <asm/io.h>
#include <asm/arch/cpu.h>
#include <asm/arch/soc.h>

#include "../drivers/ddr/marvell/a38x/ddr3_a38x_topology.h"

#include <atsha204-i2c.h>
#include <watchdog.h>


DECLARE_GLOBAL_DATA_PTR;


#if 0
#define OMNIA_ATSHA204_BUS 6
#define OMNIA_ATSHA204_OTP_MAC0_BLOCK 3
#define OMNIA_ATSHA204_OTP_MAC1_BLOCK 4
#define OMNIA_ATSHA204_OTP_VER_BLOCK 0
#define OMNIA_ATSHA204_OTP_SN_BLOCK 1 
#endif

#define OMNIA_EEPROM_BUS 0
#define OMNIA_I2C_EEPROM 0x54
#define OMNIA_I2C_EEPROM_CONFIG_ADDR 0x0
#define OMNIA_I2C_EEPROM_ADDRLEN 2
#define OMNIA_I2C_EEPROM_MAGIC 0x0341a034

#if 0
#define OMNIA_MCU_BUS 1
#define OMNIA_I2C_MCU 0x2a
#define OMNIA_I2C_MCU_WDT_ADDR 0x0b
#endif

#define ETH_PHY_CTRL_REG		0
#define ETH_PHY_CTRL_POWER_DOWN_BIT	11
#define ETH_PHY_CTRL_POWER_DOWN_MASK	(1 << ETH_PHY_CTRL_POWER_DOWN_BIT)

#define ENV_REGDOMAIN "regdomain"

/*
 * Those values and defines are taken from the Marvell U-Boot version
 * "u-boot-2013.01-2014_T3.0"
 */
#if 1
#define DB_GP_88F68XX_GPP_OUT_ENA_LOW					\
	(~(BIT(1)  | BIT(4)  | BIT(6)  | BIT(7)  | BIT(8)  | BIT(9)  |	\
	   BIT(10) | BIT(11) | BIT(19) | BIT(22) | BIT(23) | BIT(25) |	\
	   BIT(26) | BIT(27) | BIT(29) | BIT(30) | BIT(31)))
#define DB_GP_88F68XX_GPP_OUT_ENA_MID					\
	(~(BIT(0) | BIT(1) | BIT(2) | BIT(3) | BIT(4) | BIT(15) |	\
	   BIT(16) | BIT(17) | BIT(18)))
#else
#define DB_GP_88F68XX_GPP_OUT_ENA_LOW					\
	(~(BIT(1)  | BIT(4)  | BIT(6)  | BIT(7)  | BIT(8)  | BIT(9)  |	\
	   BIT(10) | BIT(11) | BIT(19) | BIT(22) | BIT(23) | BIT(25) |	\
	   BIT(26) | BIT(27) | BIT(29) | BIT(30) | BIT(31)))
#define DB_GP_88F68XX_GPP_OUT_ENA_MID					\
	(~(BIT(1) | BIT(2) | BIT(3) | BIT(13) | BIT(24)))
#endif

#define DB_GP_88F68XX_GPP_OUT_VAL_LOW	0x0
#define DB_GP_88F68XX_GPP_OUT_VAL_MID	0x0
#define DB_GP_88F68XX_GPP_POL_LOW	0x0
#define DB_GP_88F68XX_GPP_POL_MID	0x0

#define MVTWSI_ARMADA_DEBUG_REG		0x8c

/*
 * Define the DDR layout / topology here in the board file. This will
 * be used by the DDR3 init code in the SPL U-Boot version to configure
 * the DDR3 controller.
 */
static struct hws_topology_map board_topology_map_512m = {
	0x1, /* active interfaces */
	/* cs_mask, mirror, dqs_swap, ck_swap X PUPs */
	{ { { {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0} },
	    SPEED_BIN_DDR_1600K,	/* speed_bin */
	    BUS_WIDTH_16,		/* memory_width */
	    MEM_2G,			/* mem_size */
	    DDR_FREQ_800,		/* frequency */
	    0, 0,			/* cas_l cas_wl */
	    HWS_TEMP_NORMAL} },		/* temperature */
	5,				/* Num Of Bus Per Interface*/
	BUS_MASK_32BIT			/* Busses mask */
};

static struct hws_topology_map board_topology_map_1g = {
	0x1, /* active interfaces */
	/* cs_mask, mirror, dqs_swap, ck_swap X PUPs */
	{ { { {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0} },
	    SPEED_BIN_DDR_1600K,	/* speed_bin */
	    BUS_WIDTH_16,		/* memory_width */
	    MEM_4G,			/* mem_size */
	    DDR_FREQ_800,		/* frequency */
	    0, 0,			/* cas_l cas_wl */
	    HWS_TEMP_NORMAL} },		/* temperature */
	5,				/* Num Of Bus Per Interface*/
	BUS_MASK_32BIT			/* Busses mask */
};

static struct hws_topology_map board_topology_map_2g = {
	0x1, /* active interfaces */
	/* cs_mask, mirror, dqs_swap, ck_swap X PUPs */
	{ { { {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0},
	      {0x1, 0, 0, 0} },
	    SPEED_BIN_DDR_1600K,	/* speed_bin */
	    BUS_WIDTH_16,		/* memory_width */
	    MEM_8G,			/* mem_size */
	    DDR_FREQ_800,		/* frequency */
	    0, 0,			/* cas_l cas_wl */
	    HWS_TEMP_NORMAL} },		/* temperature */
	5,				/* Num Of Bus Per Interface*/
	BUS_MASK_32BIT			/* Busses mask */
};


struct omnia_eeprom {
	u32 magic;
	u32 ramsize;
	char region[4];
	u32 crc;
};

static int read_omnia_eeprom(struct omnia_eeprom *oep)
{
	int crc, retry=3;

	if (i2c_set_bus_num(OMNIA_EEPROM_BUS)) {
		puts("I2C set bus to EEPROM BUS failed\n");
		return -1;
	}

	while ((i2c_read(OMNIA_I2C_EEPROM, OMNIA_I2C_EEPROM_CONFIG_ADDR,
			OMNIA_I2C_EEPROM_ADDRLEN, (uchar *)oep,
			sizeof(struct omnia_eeprom)))&&(--retry)) {

		if (oep->magic != OMNIA_I2C_EEPROM_MAGIC) {
			puts("I2C EEPROM missing magic!\n");
			continue;
		}

		crc = crc32(0, (unsigned char *)oep, (sizeof(struct omnia_eeprom)-4));
		if (crc != oep->crc) {
			printf("CRC of EEPROM memory config failed! calc=0x%04x"
				" saved=0x%04x\n", crc, oep->crc);
			continue;
		}
	}

	if (retry <= 0) {
		puts("I2C EEPROM read failed!\n");
		return -1;
	}

	return 0;
}

#ifndef CONFIG_SPL_BUILD
static int set_regdomain(void)
{
	struct omnia_eeprom oep;
	char rd[3] = {' ', ' ', 0};

	if(!(read_omnia_eeprom(&oep)))
		memcpy(rd, &oep.region, 2);
	else
		printf("EEPROM regdomain read failed.\n");

	printf("Regdomain set to %s\n", rd);
	return setenv(ENV_REGDOMAIN, rd);
}
#endif

struct hws_topology_map *ddr3_get_topology_map(void)
{
	static int mem = 0;
	struct omnia_eeprom oep;

	/* Get the board config from EEPROM */
	if (mem == 0) {
		if(read_omnia_eeprom(&oep))
			goto out;

		printf("Memory config in EEPROM: 0x%02x\n", oep.ramsize);

#if 0
		if (oep.ramsize == 0x2)
			mem = 2;
		else
			mem = 1;
#else
		mem = oep.ramsize;
#endif
	}

	/* Hardcoded fallback */
out:	if (mem == 0 ) {
		puts("WARNING: Memory config from EEPROM read failed.\n");
		puts("Falling back to default 512MB map.\n");
		mem = 1;
	}

	/* Return the board topology as defined in the board code */
	if (mem == 1)
		return &board_topology_map_512m;
	if (mem == 2)
		return &board_topology_map_1g;
	if (mem == 3)
		return &board_topology_map_2g;

	return &board_topology_map_512m;
}

int board_early_init_f(void)
{
	u32 i2c_debug_reg;

	/* Configure MPP */
	writel(0x11111111, MVEBU_MPP_BASE + 0x00);
	writel(0x11111111, MVEBU_MPP_BASE + 0x04);
	writel(0x11244011, MVEBU_MPP_BASE + 0x08);
	writel(0x22222111, MVEBU_MPP_BASE + 0x0c);
	writel(0x22200002, MVEBU_MPP_BASE + 0x10);
	writel(0x31142022, MVEBU_MPP_BASE + 0x14);
	writel(0x55550555, MVEBU_MPP_BASE + 0x18);
	writel(0x00005550, MVEBU_MPP_BASE + 0x1c);

	/* Set GPP Out value */
	writel(DB_GP_88F68XX_GPP_OUT_VAL_LOW, MVEBU_GPIO0_BASE + 0x00);
	writel(DB_GP_88F68XX_GPP_OUT_VAL_MID, MVEBU_GPIO1_BASE + 0x00);

	/* Set GPP Polarity */
	writel(DB_GP_88F68XX_GPP_POL_LOW, MVEBU_GPIO0_BASE + 0x0c);
	writel(DB_GP_88F68XX_GPP_POL_MID, MVEBU_GPIO1_BASE + 0x0c);

	/* Set GPP Out Enable */
	writel(DB_GP_88F68XX_GPP_OUT_ENA_LOW, MVEBU_GPIO0_BASE + 0x04);
	writel(DB_GP_88F68XX_GPP_OUT_ENA_MID, MVEBU_GPIO1_BASE + 0x04);

	/* out of reset */
#if 0
	mdelay(5);
	writel(0xe, MVEBU_GPIO1_BASE + 0x00); /* GPIO_4G_RSTN(GPIO_35), GPIO_ZW_RSTN(GPIO_34), GPIO_ETH_RSTN(GPIO_33) */
	mdelay(10);
#endif

	/* Disable I2C debug mode blocking 0x64 I2C address */
	i2c_debug_reg = readl(CONFIG_I2C_MVTWSI_BASE0+MVTWSI_ARMADA_DEBUG_REG);
	i2c_debug_reg &= ~(1<<18);
	writel(i2c_debug_reg, CONFIG_I2C_MVTWSI_BASE0+MVTWSI_ARMADA_DEBUG_REG);

	return 0;
}

#if 0
#ifndef CONFIG_SPL_BUILD
static int disable_mcu_watchdog(void)
{
	uchar buf[1] = {0x0};
	int retry = 3;

	if (i2c_set_bus_num(OMNIA_MCU_BUS)) {
		puts("I2C set MCU bus failed! Can not disable MCU WDT.\n");
		return -1;
	}

	while ((i2c_write(OMNIA_I2C_MCU, OMNIA_I2C_MCU_WDT_ADDR, 1,
		(uchar *)&buf, 1))&&(--retry));

	if (retry <= 0) {
		puts("I2C MCU watchdog failed to disable!\n");
		return -2;
	}

	return 0;
}
#endif
#endif

int board_init(void)
{
	/* adress of boot parameters */
	gd->bd->bi_boot_params = mvebu_sdram_bar(0) + 0x100;

#ifndef CONFIG_SPL_BUILD
	puts("Enabling Armada 385 watchdog.\n");
	hw_watchdog_init();

#if 0
	puts("Disabling MCU startup watchdog.\n");
	disable_mcu_watchdog();
#endif

	set_regdomain();
#endif
	return 0;
}

int board_late_init(void)
{

#ifndef CONFIG_SPL_BUILD
	set_regdomain();
#endif

	return 0;
}

int checkboard(void)
{
#if 1
	printf("Board: ZL100MT (ver N/A). SN: N/A -- TODO\n");
#else
	u32 sn, ver;
	int err=0, retry=10;

	if (i2c_set_bus_num(OMNIA_ATSHA204_BUS)) {
		puts("I2C set bus to ATSHA BUS failed\n");
		err = 1;
		goto out;
	}

	while ((atsha204_wakeup() != 0)&&(--retry));
	if (retry <= 0) {
		err = 1;
		goto out;
	}

	if (atsha204_read4((u8 *)&ver, OMNIA_ATSHA204_OTP_VER_BLOCK,
			ATSHA204_OTP_REG_SELECT) != 0) {
		err = 1;
		goto out;
	}
	if (atsha204_read4((u8 *)&sn, OMNIA_ATSHA204_OTP_SN_BLOCK,
                        ATSHA204_OTP_REG_SELECT) != 0)
                err = 1;

out:
	atsha204_reset();

	if (!err)
		printf("Board: Turris Omnia SN: %08X%08X\n",
			be32_to_cpu(ver), be32_to_cpu(sn));
	else
		printf("Board: Turris Omnia (ver N/A). SN: N/A\n");
#endif

	return 0;
}

void turris_increment_mac(u8 *otp0, u8 *otp1, u8 *addr, u8 increment)
{
	u32 suffix = 0;

	suffix = otp1[3];
	suffix |= ((u32)otp1[2]) << 8;
	suffix |= ((u32)otp1[1]) << 16;

	suffix += increment;

	addr[0] = otp0[1];
	addr[1] = otp0[2];
	addr[2] = otp0[3];
	addr[3] = suffix >> 16;
	addr[4] = (suffix >> 8) & 0xFF;
	addr[5] = suffix & 0xFF;
}

int board_eth_init(bd_t *bis)
{
	u8 otp0[4], otp1[4];
	uchar addr[3][6];
	int i, err=0, retry=10;

#if 0
	/* Get the board config from ATSHA204 chip. */
	if (i2c_set_bus_num(OMNIA_ATSHA204_BUS)) {
		puts("I2C set bus to ATSHA BUS failed\n");
		err = 1;
		goto out;
	}

	while ((atsha204_wakeup() != 0)&&(--retry));
	if (retry <= 0) {
		err = 1;
		goto out;
	}

	if (atsha204_read4(otp0, OMNIA_ATSHA204_OTP_MAC0_BLOCK,
		ATSHA204_OTP_REG_SELECT) != 0) {
		err = 1;
		goto out;
	}

	if (atsha204_read4(otp1, OMNIA_ATSHA204_OTP_MAC1_BLOCK,
		ATSHA204_OTP_REG_SELECT) != 0)
		err = 1;

out:
	atsha204_reset();

	if(err != 0) {
		puts("WARNING: MAC config from ATSHA204 OTP read failed.\n");
		/* Do nothing. By default there will be random MAC addrs. */
	} else {

		for(i=0; i<3; i++)
			turris_increment_mac(otp0, otp1, addr[i], i);

		/* Set the addresses to the MAC. */
		armada385_set_mac(addr[0], addr[1], addr[2]);
	}

#else
	otp0[0] = 0;
	otp0[1] = 0xAA;
	otp0[2] = 0xBB;
	otp0[3] = 0xCC;
	otp1[0] = 0;
	otp1[1] = 0x20;
	otp1[2] = 0x19;
	otp1[3] = 0x02;

	for(i=0; i<3; i++)
		turris_increment_mac(otp0, otp1, addr[i], i);
	armada385_set_mac(addr[0], addr[1], addr[2]);
#endif
	cpu_eth_init(bis); /* Built in controller(s) come first */
	return pci_eth_init(bis);
}

