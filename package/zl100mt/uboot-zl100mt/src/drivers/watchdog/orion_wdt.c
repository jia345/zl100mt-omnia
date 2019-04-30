/*
 * drivers/watchdog/orion_wdt.c
 *
 * Watchdog driver for Orion/Kirkwood processors
 *
 * Authors:	Tomas Hlavacek <tmshlvck@gmail.com>
 * 		Sylver Bruneau <sylver.bruneau@googlemail.com>
 *
 * This file is licensed under  the terms of the GNU General Public
 * License version 2. This program is licensed "as is" without any
 * warranty of any kind, whether express or implied.
 */

#include <common.h>
#include <watchdog.h>
#include <asm/io.h>
#include <asm/arch/cpu.h>
#include <asm/arch/soc.h>


/*
 * Watchdog timer block registers.
 */

#define ORION_WDT_REG MVEBU_REGISTER(0x20300)
#define ORION_WDT_RSTOUTREG MVEBU_REGISTER(0x20704)
#define ORION_WDT_RSTOUTMASKREG MVEBU_REGISTER(0x18260)

#define RSTOUT_ENABLE_BIT BIT(8)
#define RSTOUT_MASK_BIT BIT(10)
#define WDT_ENABLE_BIT BIT(8)

#define ORION_WDT_COUNTER_OFFSET 0x34


#define TIMER_CTRL		0x0000
#define TIMER_A370_STATUS	0x04

#define WDT_MAX_CYCLE_COUNT	0xffffffff

#define WDT_AXP_FIXED_ENABLE_BIT BIT(10)
#define WDT_A370_EXPIRED	BIT(31)

#define FIXED_CLKRATE 25000000 /* Hz */
#ifndef ORION_WDT_TIMEOUT
#define ORION_WDT_TIMEOUT 120 /* sec */
#endif


static int orion_wdt_ping(void)
{
	/* Reload watchdog duration */
	writel((u32)FIXED_CLKRATE * ORION_WDT_TIMEOUT,
	       ORION_WDT_REG + ORION_WDT_COUNTER_OFFSET);
	return 0;
}

static int armada375_wdt_start(void)
{
	u32 reg;

	/* Enable the fixed watchdog clock input */
        reg = readl(ORION_WDT_REG + TIMER_CTRL);
        reg |= WDT_AXP_FIXED_ENABLE_BIT;
        writel(reg, ORION_WDT_REG + TIMER_CTRL);

	/* Set watchdog duration */
	writel((u32)FIXED_CLKRATE * ORION_WDT_TIMEOUT,
		ORION_WDT_REG + ORION_WDT_COUNTER_OFFSET);

	/* Clear the watchdog expiration bit */
	reg = readl(ORION_WDT_REG + TIMER_A370_STATUS);
	reg &= ~WDT_A370_EXPIRED;
	writel(reg, ORION_WDT_REG + TIMER_A370_STATUS);

	/* Enable watchdog timer */
	reg = readl(ORION_WDT_REG + TIMER_CTRL);
	reg |= WDT_ENABLE_BIT;
	writel(reg, ORION_WDT_REG + TIMER_CTRL);

	/* Enable reset on watchdog */
	reg = readl(ORION_WDT_RSTOUTREG);
	reg |= RSTOUT_ENABLE_BIT;
	writel(reg, ORION_WDT_RSTOUTREG);

	reg = readl(ORION_WDT_RSTOUTMASKREG);
	reg &= ~RSTOUT_MASK_BIT;
	writel(reg, ORION_WDT_RSTOUTMASKREG);
	
	return 0;
}

static int armada375_wdt_stop(void)
{
	u32 reg;

	/* Disable reset on watchdog */
	reg = readl(ORION_WDT_RSTOUTMASKREG);
	reg |= RSTOUT_MASK_BIT;
	writel(reg, ORION_WDT_RSTOUTMASKREG);

	reg = readl(ORION_WDT_RSTOUTREG);
	reg &= ~RSTOUT_ENABLE_BIT;
	writel(reg, ORION_WDT_RSTOUTREG);

	/* Disable watchdog timer */
	reg = readl(ORION_WDT_REG + TIMER_CTRL);
	reg &= ~WDT_ENABLE_BIT;
	writel(reg, ORION_WDT_REG + TIMER_CTRL);

	return 0;
}

/*
static int armada375_enabled(void)
{
	bool masked, enabled, running;

	masked = readl(ORION_WDT_RSTOUTMASKREG) & RSTOUT_MASK_BIT;
	enabled = readl(ORION_WDT_RSTOUTREG) & RSTOUT_MASK_BIT;
	running = readl(ORION_WDT_REG + TIMER_CTRL) & WDT_ENABLE_BIT;

	return !masked && enabled && running;
}
*/

void hw_watchdog_disable(void)
{
	armada375_wdt_stop();
}

void hw_watchdog_reset(void)
{
	orion_wdt_ping();
}

void hw_watchdog_init(void)
{
	armada375_wdt_start();
}

