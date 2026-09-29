This profile is licensed under AGPL-3.0, matching the reused Navet source.

The following React components are copied from [Navet](https://github.com/awesomestvi/navet):

- `src/navet/card-metric.tsx` from `packages/app/src/components/primitives/card-metric.tsx`; imports point to the local token and theme modules.
- `src/navet/entity-card-title-block.tsx` from `packages/app/src/components/primitives/entity-card-title-block.tsx`.
- `src/navet/card-metric-action-layout.tsx` from `packages/ui/src/card-metric-action-layout.tsx`.
- `src/navet/tokens.ts` contains the typography and radius token exports from `packages/app/src/components/system/tokens/foundations.ts`.

The static preview supplies CSS for the utility classes these primitives use. Its dark palette and card geometry follow Navet's theme and BaseCard tokens. GitHub images use a Pillow render of that composition.

Inter is distributed under the SIL Open Font License; see `assets/fonts/LICENSE.txt`. The bundled TrueType file is converted from Navet's Inter WOFF2 asset.
