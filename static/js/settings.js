export function settings_list() {
    const select = document.getElementById('settings_select');
    select.addEventListener('change', async function(e) {
        const response = await fetch(`/get_settings/${e.target.value}`);
        if (response.ok) {
            const data = await response.json();
            document.getElementById('height').value = data.height;
            document.getElementById('width').value = data.width;
            document.getElementById('speed').value = data.speed;
            document.getElementById('I_color').value = data.figure_colors.I;
            document.getElementById('O_color').value = data.figure_colors.O;
            document.getElementById('T_color').value = data.figure_colors.T;
            document.getElementById('L_color').value = data.figure_colors.L;
            document.getElementById('J_color').value = data.figure_colors.J;
            document.getElementById('S_color').value = data.figure_colors.S;
            document.getElementById('Z_color').value = data.figure_colors.Z;
        }
    });

    const del = document.getElementById('S_delete');
    const msg = document.getElementById('S_msg');
    del.addEventListener('click', async () => {
        const settingsId = select.value;
        if (!settingsId) {
            msg.textContent = 'Выберите настройки для удаления'
            return;
        }
        try {
            const response = await fetch(`/api/settings/${settingsId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            if (response.ok) {
                del.disabled = true;
                msg.textContent = data.message
                setTimeout(() => location.reload(), 1000);
            }
            else{
                msg.textContent = data.error
            }
        } catch (error) {
            msg.textContent = data.error
        }
    });
}