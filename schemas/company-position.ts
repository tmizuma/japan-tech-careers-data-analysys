import { z } from "zod";

// Position スキーマ
export const PositionSchema = z.object({
  name: z.string(),
  link: z.string(),
});

// CompanyData スキーマ
export const CompanyDataSchema = z.object({
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
  positions: z.array(PositionSchema),
});

// 型エクスポート
export type Position = z.infer<typeof PositionSchema>;
export type CompanyData = z.infer<typeof CompanyDataSchema>;
