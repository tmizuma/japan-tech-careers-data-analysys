#!/usr/bin/env npx ts-node
import { RankingSchema } from "../schemas/ranking";
import * as fs from "fs";

const files = ["current/sales_ranking.json", "current/position_ranking.json"];

for (const file of files) {
  if (!fs.existsSync(file)) {
    console.log(`✗ ${file} (not found)`);
    continue;
  }
  const data = JSON.parse(fs.readFileSync(file, "utf-8"));
  const result = RankingSchema.safeParse(data);
  if (result.success) {
    console.log(`✓ ${file}`);
  } else {
    console.log(`✗ ${file}`);
    for (const issue of result.error.issues) {
      console.log(`  - ${issue.path.join(".")}: ${issue.message}`);
    }
  }
}
