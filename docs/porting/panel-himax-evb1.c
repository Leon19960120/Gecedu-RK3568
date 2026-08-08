// SPDX-License-Identifier: GPL-2.0
/*
 * Panel driver for the 7-inch MIPI-DSI display on the
 * Rockchip RK3568 EVB1 DDR4 V10 board (Yueqian / GEC RK3568).
 *
 * WHY THIS DRIVER EXISTS
 * ----------------------
 * The panel is built around a Himax controller, but its SETEXTC unlock
 * password (B9 F1 12 83) matches NO mainline Himax driver
 * (hx8394 = FF 83 94, hx83102 = 83 10 21, hx83112a = 83 11 2a, hx8279 = ...).
 * The init sequence below was lifted VERBATIM from the board's extracted
 * device tree (the `panel-init-sequence` property of the dsi0 panel node)
 * and is replayed in prepare().
 *
 * IMPORTANT: the vendor `panel-init-sequence` is a Rockchip BSP *private*
 * property that mainline `panel-simple` ignores. You cannot reuse the
 * downstream DTS as-is -- this driver is the portable replacement.
 *
 * Display: 1024x600 @ 60 Hz, 4 DSI data lanes, pixel clock 51.2 MHz.
 * Panel reset: GPIO3_A7 (LRSTB), active-high per DTS flag.
 * LCD power enable: vcc3v3-lcd0-n, a gpio-regulator on GPIO0_C7.
 * Backlight: pwm5 (pwm@fe6e0010). NOTE: mainline rk3568-evb1-v10.dts uses
 * &pwm4, so the backlight index must be adjusted when porting.
 */

#include <linux/delay.h>
#include <linux/gpio/consumer.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/regulator/consumer.h>

#include <drm/drm_mipi_dsi.h>
#include <drm/drm_modes.h>
#include <drm/drm_panel.h>

struct gec_panel {
	struct drm_panel panel;
	struct mipi_dsi_device *dsi;
	struct regulator *power;
	struct gpio_desc *reset;
	struct gpio_desc *enable;
	struct backlight_device *backlight;
};

static inline struct gec_panel *to_gec_panel(struct drm_panel *p)
{
	return container_of(p, struct gec_panel, panel);
}

static int gec_panel_prepare(struct drm_panel *panel)
{
	struct gec_panel *ctx = to_gec_panel(panel);
	struct mipi_dsi_device *dsi = ctx->dsi;
	int ret;

	if (ctx->power) {
		ret = regulator_enable(ctx->power);
		if (ret)
			return ret;
	}
	if (ctx->enable)
		gpiod_set_value_cansleep(ctx->enable, 1);

	/* reset pulse: DTS flag ACTIVE_HIGH -> assert high, then release */
	if (ctx->reset) {
		gpiod_set_value_cansleep(ctx->reset, 1);
		msleep(20);
		gpiod_set_value_cansleep(ctx->reset, 0);
		msleep(20);
	}

	/* [00] DCS 0x11 (type 0x05), post-delay 250 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0x11);
	if (ret)
		return ret;
	msleep(250);

	/* [01] DCS 0xb9 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xb9, 0xf1, 0x12, 0x83);
	if (ret)
		return ret;
	/* no delay specified */

	/* [02] DCS 0xba (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xba, 0x33, 0x81, 0x05, 0xf9, 0x0e, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x44, 0x25, 0x00, 0x91, 0x0a, 0x00, 0x00, 0x02, 0x4f, 0x01, 0x00, 0x00, 0x37);
	if (ret)
		return ret;
	/* no delay specified */

	/* [03] DCS 0xb8 (type 0x15), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xb8, 0x25);
	if (ret)
		return ret;
	/* no delay specified */

	/* [04] DCS 0xbf (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xbf, 0x02, 0x11, 0x00);
	if (ret)
		return ret;
	/* no delay specified */

	/* [05] DCS 0xb3 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xb3, 0x0c, 0x10, 0x0a, 0x50, 0x03, 0xff, 0x00, 0x00, 0x00, 0x00);
	if (ret)
		return ret;
	/* no delay specified */

	/* [06] DCS 0xc0 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xc0, 0x73, 0x73, 0x50, 0x50, 0x00, 0x00, 0x08, 0x70, 0x00);
	if (ret)
		return ret;
	/* no delay specified */

	/* [07] DCS 0xbc (type 0x15), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xbc, 0x46);
	if (ret)
		return ret;
	/* no delay specified */

	/* [08] DCS 0xcc (type 0x15), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xcc, 0x0b);
	if (ret)
		return ret;
	/* no delay specified */

	/* [09] DCS 0xb4 (type 0x15), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xb4, 0x80);
	if (ret)
		return ret;
	/* no delay specified */

	/* [10] DCS 0xb2 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xb2, 0xc8, 0x12, 0x30);
	if (ret)
		return ret;
	/* no delay specified */

	/* [11] DCS 0xe3 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xe3, 0x07, 0x07, 0x0b, 0x0b, 0x03, 0x0b, 0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0xc0, 0x10);
	if (ret)
		return ret;
	/* no delay specified */

	/* [12] DCS 0xc1 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xc1, 0x53, 0x00, 0x1e, 0x1e, 0x77, 0xe1, 0xcc, 0xdd, 0x67, 0x77, 0x33, 0x33);
	if (ret)
		return ret;
	/* no delay specified */

	/* [13] DCS 0xc6 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xc6, 0x00, 0x00, 0xff, 0xff, 0x01, 0xff);
	if (ret)
		return ret;
	/* no delay specified */

	/* [14] DCS 0xb5 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xb5, 0x09, 0x09);
	if (ret)
		return ret;
	/* no delay specified */

	/* [15] DCS 0xb6 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xb6, 0x87, 0x95);
	if (ret)
		return ret;
	/* no delay specified */

	/* [16] DCS 0xe9 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xe9, 0xc2, 0x10, 0x05, 0x05, 0x10, 0x05, 0xa0, 0x12, 0x31, 0x23, 0x3f, 0x81, 0x0a, 0xa0, 0x37, 0x18, 0x00, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00, 0x80, 0x01, 0x00, 0x00, 0x00, 0x48, 0xf8, 0x86, 0x42, 0x08, 0x88, 0x88, 0x80, 0x88, 0x88, 0x88, 0x58, 0xf8, 0x87, 0x53, 0x18, 0x88, 0x88, 0x81, 0x88, 0x88, 0x88, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00);
	if (ret)
		return ret;
	/* no delay specified */

	/* [17] DCS 0xea (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xea, 0x00, 0x1a, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1f, 0x88, 0x81, 0x35, 0x78, 0x88, 0x88, 0x85, 0x88, 0x88, 0x88, 0x0f, 0x88, 0x80, 0x24, 0x68, 0x88, 0x88, 0x84, 0x88, 0x88, 0x88, 0x23, 0x10, 0x00, 0x00, 0x1c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30, 0x05, 0xa0, 0x00, 0x00, 0x00, 0x00);
	if (ret)
		return ret;
	/* no delay specified */

	/* [18] DCS 0xe0 (type 0x39), post-delay 0 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0xe0, 0x00, 0x06, 0x08, 0x2a, 0x31, 0x3f, 0x38, 0x36, 0x07, 0x0c, 0x0d, 0x11, 0x13, 0x12, 0x13, 0x11, 0x18, 0x00, 0x06, 0x08, 0x2a, 0x31, 0x3f, 0x38, 0x36, 0x07, 0x0c, 0x0d, 0x11, 0x13, 0x12, 0x13, 0x11, 0x18);
	if (ret)
		return ret;
	/* no delay specified */

	/* [19] DCS 0x29 (type 0x05), post-delay 50 */
	ret = mipi_dsi_dcs_write_seq(dsi, 0x29);
	if (ret)
		return ret;
	msleep(50);


	return 0;
}

static int gec_panel_enable(struct drm_panel *panel)
{
	struct gec_panel *ctx = to_gec_panel(panel);

	if (ctx->backlight) {
		ctx->panel.backlight->props.power = FB_BLANK_UNBLANK;
		backlight_update_status(ctx->backlight);
	}
	return 0;
}

static int gec_panel_disable(struct drm_panel *panel)
{
	struct gec_panel *ctx = to_gec_panel(panel);

	if (ctx->backlight) {
		ctx->panel.backlight->props.power = FB_BLANK_POWERDOWN;
		backlight_update_status(ctx->backlight);
	}
	return 0;
}

static int gec_panel_unprepare(struct drm_panel *panel)
{
	struct gec_panel *ctx = to_gec_panel(panel);
	struct mipi_dsi_device *dsi = ctx->dsi;
	int ret;

	/* exit sequence from DTS: display off (0x28) then sleep in (0x10) */
	ret = mipi_dsi_dcs_set_display_off(dsi);
	if (ret)
		return ret;
	msleep(50);
	ret = mipi_dsi_dcs_enter_sleep_mode(dsi);
	if (ret)
		return ret;
	msleep(120);

	if (ctx->reset)
		gpiod_set_value_cansleep(ctx->reset, 1);
	if (ctx->enable)
		gpiod_set_value_cansleep(ctx->enable, 0);
	if (ctx->power)
		regulator_disable(ctx->power);

	return 0;
}

static const struct drm_display_mode gec_default_mode = {
	.clock = 51200, /* kHz (51.2 MHz) */
	.hdisplay = 1024,
	.hsync_start = 1024 + 160,
	.hsync_end = 1024 + 160 + 2,
	.htotal = 1024 + 160 + 2 + 160,
	.vdisplay = 600,
	.vsync_start = 600 + 12,
	.vsync_end = 600 + 12 + 2,
	.vtotal = 600 + 12 + 2 + 23,
	.width_mm = 154,
	.height_mm = 90,
	.flags = DRM_MODE_FLAG_NHSYNC | DRM_MODE_FLAG_NVSYNC,
	.type = DRM_MODE_TYPE_DRIVER | DRM_MODE_TYPE_PREFERRED,
};

static int gec_panel_get_modes(struct drm_panel *panel,
			       struct drm_connector *connector)
{
	struct gec_panel *ctx = to_gec_panel(panel);
	struct drm_display_mode *mode;

	mode = drm_mode_duplicate(connector->dev, &gec_default_mode);
	if (!mode)
		return -ENOMEM;

	drm_mode_set_name(mode);
	mode->bus_flags = DRM_BUS_FLAG_DE_LOW;
	/* pixelclk-active = 0 in DTS -> data sampled on falling edge;
	 * verify against the panel spec if the image is shifted. */
	drm_mode_probed_add(connector, mode);

	connector->display_info.width_mm = mode->width_mm;
	connector->display_info.height_mm = mode->height_mm;
	connector->display_info.bpc = 8;

	return 1;
}

static const struct drm_panel_funcs gec_panel_funcs = {
	.prepare = gec_panel_prepare,
	.enable = gec_panel_enable,
	.disable = gec_panel_disable,
	.unprepare = gec_panel_unprepare,
	.get_modes = gec_panel_get_modes,
};

static int gec_panel_probe(struct mipi_dsi_device *dsi)
{
	struct gec_panel *ctx;
	int ret;

	ctx = devm_kzalloc(&dsi->dev, sizeof(*ctx), GFP_KERNEL);
	if (!ctx)
		return -ENOMEM;

	ctx->dsi = dsi;
	mipi_dsi_set_drvdata(dsi, ctx);

	ctx->power = devm_regulator_get_optional(&dsi->dev, "power");
	if (IS_ERR(ctx->power)) {
		ret = PTR_ERR(ctx->power);
		if (ret != -ENODEV)
			return ret;
		ctx->power = NULL;
	}
	ctx->reset = devm_gpiod_get_optional(&dsi->dev, "reset", GPIOD_OUT_LOW);
	if (IS_ERR(ctx->reset))
		return PTR_ERR(ctx->reset);
	ctx->enable = devm_gpiod_get_optional(&dsi->dev, "enable", GPIOD_OUT_LOW);
	if (IS_ERR(ctx->enable))
		return PTR_ERR(ctx->enable);

	/* backlight is obtained via drm_panel_of_backlight() below */

	drm_panel_init(&ctx->panel, &dsi->dev, &gec_panel_funcs,
		       DRM_MODE_CONNECTOR_DSI);
	ctx->panel.prepare_prev_first = true;

	ret = drm_panel_of_backlight(&ctx->panel);
	if (ret)
		return ret;

	drm_panel_add(&ctx->panel);

	dsi->lanes = 4;
	dsi->format = MIPI_DSI_FMT_RGB888;
	dsi->mode_flags = MIPI_DSI_MODE_VIDEO | MIPI_DSI_MODE_VIDEO_BURST |
			  MIPI_DSI_MODE_LPM;

	ret = mipi_dsi_attach(dsi);
	if (ret) {
		drm_panel_remove(&ctx->panel);
		return ret;
	}

	return 0;
}

static void gec_panel_remove(struct mipi_dsi_device *dsi)
{
	struct gec_panel *ctx = mipi_dsi_get_drvdata(dsi);

	mipi_dsi_detach(dsi);
	drm_panel_remove(&ctx->panel);
}

static const struct of_device_id gec_panel_of_match[] = {
	{ .compatible = "gec,rk3568-evb1-dsi-panel" },
	{ /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, gec_panel_of_match);

static struct mipi_dsi_driver gec_panel_driver = {
	.driver = {
		.name = "gec-rk3568-evb1-dsi-panel",
		.of_match_table = gec_panel_of_match,
	},
	.probe = gec_panel_probe,
	.remove = gec_panel_remove,
};
module_mipi_dsi_driver(gec_panel_driver);

MODULE_AUTHOR("GEC-RK3568 porting effort");
MODULE_DESCRIPTION("Himax-based 7\" MIPI-DSI panel on RK3568 EVB1 DDR4 V10");
MODULE_LICENSE("GPL");
