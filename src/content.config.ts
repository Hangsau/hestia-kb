// Content collection schema — W2.2
// 驗 vault .md 的 frontmatter 結構
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const notes = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/notes' }),
  schema: z
    .object({
      _slug: z.string(),
      _vault_path: z.string().optional(),
      title: z.string(),
      type: z.string().default('note'),
      status: z.enum(['seedling', 'budding', 'evergreen']).default('seedling'),
      tags: z.array(z.string()).default([]),
      created: z.string().optional(),
      updated: z.string().optional(),
    })
    // 其餘欄位全部寬鬆（vault 格式太雜，全拒就沒了）
    .passthrough(),
});

export const collections = { notes };
