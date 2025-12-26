#!/usr/bin/env npx ts-node
import * as fs from "fs";
import * as path from "path";
import { CompanyDataSchema } from "../schemas/company-position";

const targetDir = process.argv[2] || "202512";

if (!fs.existsSync(targetDir)) {
  console.error(`Error: Directory "${targetDir}" does not exist.`);
  process.exit(1);
}

const jsonFiles = fs.readdirSync(targetDir).filter((f) => f.endsWith(".json"));

if (jsonFiles.length === 0) {
  console.error(`No JSON files found in "${targetDir}".`);
  process.exit(1);
}

console.log(`Validating ${jsonFiles.length} JSON files in ${targetDir}/\n`);

let validCount = 0;
let invalidCount = 0;
const errors: { file: string; issues: string[] }[] = [];

for (const file of jsonFiles) {
  const filePath = path.join(targetDir, file);
  try {
    const content = fs.readFileSync(filePath, "utf-8");
    const data = JSON.parse(content);
    const result = CompanyDataSchema.safeParse(data);

    if (result.success) {
      console.log(`✓ ${file}`);
      validCount++;
    } else {
      console.log(`✗ ${file}`);
      const issues = result.error.issues.map(
        (issue) => `  - ${issue.path.join(".")}: ${issue.message}`
      );
      errors.push({ file, issues });
      invalidCount++;
    }
  } catch (e) {
    console.log(`✗ ${file}`);
    const message = e instanceof Error ? e.message : String(e);
    errors.push({ file, issues: [`  - Parse error: ${message}`] });
    invalidCount++;
  }
}

console.log("\n" + "=".repeat(50));
console.log(`Results: ${validCount} valid, ${invalidCount} invalid`);

if (errors.length > 0) {
  console.log("\nErrors:");
  for (const { file, issues } of errors) {
    console.log(`\n${file}:`);
    for (const issue of issues) {
      console.log(issue);
    }
  }
  process.exit(1);
}

console.log("\nAll files are valid!");
