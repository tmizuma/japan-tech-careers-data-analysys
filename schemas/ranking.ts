import { z } from "zod";

// ランキング用の企業データスキーマ（positionsの代わりにnum_of_positionsを持つ）
export const RankedCompanySchema = z.object({
  company_name_ja: z.string(),
  company_name_en: z.string(),
  description: z.string(),
  description_en: z.string(),
  hiring_url: z.string(),
  num_of_employees: z.string(),
  sales: z.number().int(),
  foreign_engineers: z.boolean(),
  logo_url: z.string(),
  company_url: z.string(),
  num_of_positions: z.number().int(),
});

// ランキングJSONスキーマ
export const RankingSchema = z.object({
  companies: z.record(z.string(), RankedCompanySchema),
});

// 型エクスポート
export type RankedCompany = z.infer<typeof RankedCompanySchema>;
export type Ranking = z.infer<typeof RankingSchema>;
