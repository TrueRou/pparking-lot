export const config = {
    backend_entrypoint: "https://osu.ppy.sb/performance/api/",
};

export const requests = {
    scores_global: new URL("scores/global", config.backend_entrypoint).href,
    scores_mode: new URL("scores/mode", config.backend_entrypoint).href,
    scores_player: new URL("scores/player", config.backend_entrypoint).href,
    scores_analysis: new URL("scores/analysis", config.backend_entrypoint).href
};