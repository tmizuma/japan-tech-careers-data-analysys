#!/usr/bin/env npx ts-node
import * as fs from "fs";
import { CompanyDataSchema } from "../schemas/company-position";

const filePath = process.argv[2];
if (!filePath) {
  console.error("Usage: npx ts-node scripts/validate-company.ts <json-file>");
  process.exit(1);
}

const content = fs.readFileSync(filePath, "utf-8");
const data = JSON.parse(content);
const result = CompanyDataSchema.safeParse(data);

if (!result.success) {
  console.error("INVALID:", filePath);
  for (const issue of result.error.issues) {
    console.error(`  - ${issue.path.join(".")}: ${issue.message}`);
  }
  process.exit(1);
}

console.log("VALID:", filePath);
