export const figures = {
    "O": [[1, 1], [1, 1],],
    "I": [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    "S": [[0, 1, 1], [1, 1, 0], [0, 0, 0],],
    "Z": [[1, 1, 0], [0, 1, 1], [0, 0, 0],],
    "L": [[0, 0, 1], [1, 1, 1], [0, 0, 0],],
    "J": [[1, 0, 0], [1, 1, 1], [0, 0, 0],],
    "T": [[0, 1, 0], [1, 1, 1], [0, 0, 0],]
};

export async function change_consts() {
    const response = await fetch('/api/change_settings');
    const gamesettings = await response.json();
    const colors = { ...gamesettings.figure_colors };
    const game_settings = {
        stl: gamesettings.width,
        str: gamesettings.height,
        speed: gamesettings.speed
    };
    return { colors, game_settings };
}