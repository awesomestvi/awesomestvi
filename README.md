<img src="assets/dashboard.gif" alt="Vishal Chauhan's animated GitHub activity dashboard: a real contribution heatmap, commit and pull request counts, active days, longest streak, weekly activity, and language mix." width="100%" />

<p align="center">
  <a href="https://github.com/awesomestvi?tab=repositories">Repositories</a> ·
  <a href="https://github.com/awesomestvi/navet">Building Navet</a> ·
  <a href="assets/dashboard.png">Still image</a>
</p>

I'm **Vishal Chauhan**, a frontend developer and UI/UX designer. I build [Navet](https://github.com/awesomestvi/navet), a smart-home dashboard.

**TypeScript · React · CSS · UI/UX**

<details>
<summary>Behind the pixels</summary>

The heatmap and statistics come from GitHub's API. Activity covers GitHub's trailing-year contribution window; longest streak counts consecutive days with contributions in that window. Language percentages use GitHub-reported bytes across public, owned repositories, excluding forks. Stars are summed across those same repositories.

The animated comet and chart trace are visual effects. The underlying contribution values stay fixed. The footer shows the snapshot date. A daily GitHub Action refreshes the data and images; scheduled runs can be delayed by GitHub. Use the **Still image** link above for a motion-free view.

The repository includes an interactive preview with a motion pause button and reduced-motion support:

```sh
python3 -m http.server 8099
```

Open `http://localhost:8099`. On a small screen, scroll the calendar horizontally to explore the full year. Hover a cell for its date and contribution count.

To refresh locally, authenticate the GitHub CLI, then run:

```sh
npm ci --ignore-scripts
python3 -m pip install -r requirements.txt
python3 scripts/update_profile.py
npm run build:components
python3 scripts/render_dashboard.py
```

The preview reuses Navet’s `CardMetric`, `CardMetricActionLayout`, and `EntityCardTitleBlock` React primitives. They are rendered into static fragments before serving. The image renderer uses the same font, metric hierarchy, and card geometry with Pillow. Set `PROFILE_FONT_REGULAR` and `PROFILE_FONT_BOLD` to custom font paths if desired. The repository contains a public activity snapshot; credentials stay in GitHub CLI authentication or the Actions environment.

</details>
