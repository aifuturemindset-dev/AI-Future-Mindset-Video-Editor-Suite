import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer("swangle");

// The sandbox cannot grant Chromium its own sandbox, and remotion.media is
// blocked by the egress allowlist, so renders here reuse the preinstalled
// headless shell. On a normal machine neither line is needed.
Config.setChromiumDisableWebSecurity(true);
