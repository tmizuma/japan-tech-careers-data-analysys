import * as fs from "fs";
import * as path from "path";
import { CompanyDataSchema } from "../schemas/company-position";

const targetDir = process.argv[2] || "202512";
const outputFile = "research.txt";

const jsonFiles = fs
  .readdirSync(targetDir)
  .filter((file) => file.endsWith(".json"));

const invalidFiles: { file: string; errors: string[] }[] = [];

for (const file of jsonFiles) {
  const filePath = path.join(targetDir, file);
  const content = fs.readFileSync(filePath, "utf-8");

  try {
    const data = JSON.parse(content);
    const result = CompanyDataSchema.safeParse(data);

    if (!result.success) {
      const errors = result.error.issues.map((issue) => {
        const path = issue.path.join(".");
        return `  - ${path}: ${issue.message} (expected: ${issue.code})`;
      });
      invalidFiles.push({ file, errors });
    }
  } catch (e) {
    invalidFiles.push({ file, errors: [`  - JSON parse error: ${e}`] });
  }
}

// 結果を出力
const output: string[] = [];
output.push(`# 型不一致JSONファイル一覧`);
output.push(`# 検証対象: ${targetDir}/`);
output.push(`# 総ファイル数: ${jsonFiles.length}`);
output.push(`# 不一致ファイル数: ${invalidFiles.length}`);
output.push(``);

if (invalidFiles.length === 0) {
  output.push(`すべてのファイルが型に一致しています。`);
} else {
  for (const { file, errors } of invalidFiles) {
    output.push(`## ${file}`);
    output.push(errors.join("\n"));
    output.push(``);
  }
}

fs.writeFileSync(outputFile, output.join("\n"));
console.log(`結果を ${outputFile} に出力しました。`);
console.log(`不一致ファイル数: ${invalidFiles.length}/${jsonFiles.length}`);
