export const config = {
    backend_entrypoint: "http://127.0.0.1:8000/",
};

export var requests = {
    scores_global: config.backend_entrypoint + "scores/global",
    scores_mode: config.backend_entrypoint + "scores/mode",
    scores_player: config.backend_entrypoint + "scores/player",
    scores_analysis: config.backend_entrypoint + "scores/analysis"
};