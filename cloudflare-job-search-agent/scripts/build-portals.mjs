#!/usr/bin/env node

/**
 * build-portals.mjs — regenerate the portals config bundled into JobSearchAgent.
 *
 * Reads a portals YAML file and writes the three keys the agent needs
 * (tracked_companies + title_filter + location_filter) as JSON into
 * src/agents/job-search.portals.json. Re-run whenever your portals file changes.
 *
 * Usage:
 *   node scripts/build-portals.mjs                     # reads portals.yml in project root
 *   node scripts/build-portals.mjs /path/to/portals.yml
 */

import { readFileSync, writeFileSync } from "fs";
import yaml from "js-yaml";

const SOURCE = process.argv[2] ?? "portals.yml";
const OUT = "src/agents/job-search.portals.json";

const config = yaml.load(readFileSync(SOURCE, "utf-8"));

const portals = {
  tracked_companies: config.tracked_companies ?? [],
  title_filter: config.title_filter ?? { positive: [], negative: [] },
  location_filter: config.location_filter ?? { positive: [], negative: [] }
};

writeFileSync(OUT, `${JSON.stringify(portals, null, 2)}\n`, "utf-8");

const enabled = portals.tracked_companies.filter((c) => c.enabled !== false).length;
console.log(`Wrote ${OUT}`);
console.log(`  companies:       ${portals.tracked_companies.length} (${enabled} enabled)`);
console.log(
  `  title_filter:    +${portals.title_filter.positive?.length ?? 0} / -${portals.title_filter.negative?.length ?? 0}`
);
console.log(
  `  location_filter: +${portals.location_filter.positive?.length ?? 0} / -${portals.location_filter.negative?.length ?? 0}`
);
