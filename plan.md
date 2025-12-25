# Zod を使った型安全な JSON 出力の実装計画

## 問題

`gather-japan-position-info` コマンド実行時に、Claude Code が勝手にフィールドを追加・削除してしまう。

**例: astroscale.json に欠けているフィールド:**
- `description`, `description_en`
- `hiring_url`, `num_of_employees`, `sales`, `foreign_engineers`
- `logo_url`, `company_url`

## 解決策

Zod スキーマを定義し、コマンドの指示に組み込むことで、型の一致を保証する。

## TypeScript 型定義

### Position 型

```typescript
interface Position {
  name: string;           // 求人タイトル
  description: string;    // 一覧ページの説明文（最大500文字）
  techstack: string[];    // 技術スタック（空配列可）
  link: string;           // 求人ページURL
}
```

### CompanyData 型（基本）

```typescript
interface CompanyData {
  company_name_ja: string;    // 企業名（日本語）
  company_name_en: string;    // 企業名（英語）
  description: string;        // 企業説明（日本語）
  description_en: string;     // 企業説明（英語）
  hiring_url: string;         // 採用ページURL
  num_of_employees: string;   // 従業員数（例: "100+", "2000+"）
  sales: number;              // 売上高（円）。不明の場合は -1
  foreign_engineers: boolean; // 外国人エンジニア採用実績
  logo_url: string;           // ロゴ画像URL
  company_url: string;        // 企業サイトURL
  positions: Position[];      // 求人情報リスト
}
```

### エラー処理

エラー時は JSON ファイルを作成せず、`{yyyymm}/error.log` に出力する。
チェックリストは未完了のままにする。

```
[2024-12-25 10:30:00] astroscale: CONNECTION_ERROR - Failed to connect to https://...
[2024-12-25 10:31:00] somecompany: PARSE_ERROR - Failed to parse job listings
```

## Zod スキーマ定義

```typescript
import { z } from "zod";

// Position スキーマ
const PositionSchema = z.object({
  name: z.string(),
  description: z.string(),
  techstack: z.array(z.string()),
  link: z.string().url(),
});

// CompanyData スキーマ（必須フィールドのみ）
const CompanyDataSchema = z.object({
  company_name_ja: z.string(),
  company_name_en: z.string(),
  description: z.string(),
  description_en: z.string(),
  hiring_url: z.string().url(),
  num_of_employees: z.string(),
  sales: z.number().int(),
  foreign_engineers: z.boolean(),
  logo_url: z.string().url(),
  company_url: z.string().url(),
  positions: z.array(PositionSchema),
});

// 型エクスポート
type Position = z.infer<typeof PositionSchema>;
type CompanyData = z.infer<typeof CompanyDataSchema>;
```

## 実装手順

### Step 1: スキーマファイルの作成

`schemas/company-position.ts` を作成し、上記の Zod スキーマを定義する。

### Step 2: コマンドファイルの修正

`.claude/commands/gather-japan-position-info.md` を修正:

1. **スキーマ参照の追加**: コマンド冒頭でスキーマファイルを参照するよう指示
2. **バリデーション指示の追加**: JSON 出力前に必ずスキーマでバリデーションを行うよう明記
3. **全フィールド必須の強調**: スキーマに定義された全フィールドを必ず含めることを強調

### Step 3: コマンドに追加する指示文

```markdown
## スキーマ定義

**【重要】JSON 出力は以下の Zod スキーマに厳密に従うこと:**

`schemas/company-position.ts` を参照し、出力する JSON が以下の条件を満たすことを保証してください:

1. `CompanyDataSchema` の全フィールドが存在すること
2. フィールドの追加・削除は禁止
3. データ型が一致すること（sales は number, foreign_engineers は boolean）
4. positions 配列の各要素が `PositionSchema` に準拠すること
```

## ファイル変更一覧

| ファイル | 変更内容 |
|---------|---------|
| `schemas/company-position.ts` | 新規作成: Zod スキーマ定義 |
| `.claude/commands/gather-japan-position-info.md` | スキーマ参照とバリデーション指示の追加 |
