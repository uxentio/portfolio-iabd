// Recorder de las acciones del usuario sobre el formulario.
// Recibe la metadata del workflow por constructor para reusarse en otros forms.

class FormRecorder {
    /**
     * @param {Object} workflowMeta  campos fijos del workflow (id, titulo, descripcion, app, url, tags, param_schema)
     * @param {Object} fieldPlaceholders  mapa name/id -> "{{var}}" para sustituir valores tecleados
     * @param {Object} ui  ids de los elementos del panel (start, stop, download, indicator, count)
     */
    constructor(workflowMeta, fieldPlaceholders, ui) {
        this.meta = workflowMeta;
        this.placeholders = fieldPlaceholders;
        this.ui = ui;
        this.recording = false;
        this.steps = [];

        // Bind aquí para que removeEventListener encuentre las funciones al parar.
        this._onClick = this._handleClick.bind(this);
        this._onInput = this._handleInput.bind(this);
        this._onChange = this._handleChange.bind(this);
    }

    // Selector estable: #id, luego [name="..."]. Nada de XPath.
    _selector(el) {
        if (el.id) return '#' + el.id;
        if (el.name) return `[name="${el.name}"]`;
        return el.tagName.toLowerCase();
    }

    _placeholderFor(el) {
        const key = el.name || el.id;
        return this.placeholders[key] ?? el.value;
    }

    // Filtra eventos que ocurren dentro del propio panel del recorder.
    // Sin esto, el click sobre Stop entra en captura ANTES que el onclick
    // que llama a stop(), y se cuela como paso espurio en el workflow
    // (un #btn_stop que solo existe en este panel, no en producción).
    _esEventoDelPanel(e) {
        return !!(e.target && e.target.closest && e.target.closest('.recorder-card'));
    }

    // Refresca contador + timeline en una sola llamada. Lo invocan los tres
    // handlers para que el usuario vea en directo la lista de pasos sin
    // tener que esperar a Stop.
    _refresh() {
        this._refreshCount();
        this._renderSteps();
    }

    _handleClick(e) {
        if (!this.recording) return;
        if (this._esEventoDelPanel(e)) return;
        // Inputs/select/textarea ya disparan input/change; aquí solo clicks "puros".
        const tag = e.target.tagName;
        if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;
        this.steps.push({ type: 'click', target: { by: 'css', value: this._selector(e.target) } });
        this._refresh();
    }

    _handleInput(e) {
        if (!this.recording) return;
        if (this._esEventoDelPanel(e)) return;
        const tag = e.target.tagName;
        if (tag !== 'INPUT' && tag !== 'TEXTAREA') return;
        const sel = this._selector(e.target);
        const value = this._placeholderFor(e.target);
        // Deduplico: si el usuario corrige, me quedo solo con el último.
        this.steps = this.steps.filter(s => !(s.type === 'type' && s.target.value === sel));
        this.steps.push({ type: 'type', target: { by: 'css', value: sel }, value });
        this._refresh();
    }

    _handleChange(e) {
        if (!this.recording) return;
        if (this._esEventoDelPanel(e)) return;
        if (e.target.tagName !== 'SELECT') return;
        const sel = this._selector(e.target);
        const value = this._placeholderFor(e.target);
        this.steps.push({ type: 'select', target: { by: 'css', value: sel }, value });
        this._refresh();
    }

    _refreshCount() {
        const el = document.getElementById(this.ui.count);
        if (el) {
            const n = this.steps.length;
            el.textContent = n === 0 ? '' : `${n} ${n === 1 ? 'paso' : 'pasos'}`;
        }
    }

    // Estados visuales del pill: idle / active / success.
    // El recolector visual lo lleva la clase CSS; aquí solo cambiamos modificador y texto.
    _setStatus(estado, texto) {
        const el = document.getElementById(this.ui.indicator);
        if (!el) return;
        el.classList.remove('active', 'success');
        if (estado === 'active' || estado === 'success') {
            el.classList.add(estado);
        }
        const txt = document.getElementById(this.ui.statusText);
        if (txt) txt.textContent = texto;
    }

    // HTML escape básico para no romper la timeline si un selector lleva caracteres raros.
    _esc(s) {
        return String(s ?? '').replace(/[&<>"']/g, c => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
        }[c]));
    }

    // Cada step se renderiza como una fila del timeline con: número, badge
    // del tipo (click/type/select/wait/text) y el detalle. El badge es lo
    // que da el color de un vistazo y permite escanear la grabación rápido.
    _renderSteps() {
        if (!this.ui.stepsList) return;
        const cont = document.getElementById(this.ui.stepsList);
        if (!cont) return;

        const header = '<div class="rec-steps-header">Pasos grabados</div>';
        if (this.steps.length === 0) {
            cont.classList.remove('show');
            cont.innerHTML = header;
            return;
        }

        const filaPara = (s, i) => {
            let badge = '', cls = '', detail = '';
            switch (s.type) {
                case 'click':
                    badge = 'click';   cls = 'rec-type-click';
                    detail = `<span class="arg">${this._esc(s.target.value)}</span>`;
                    break;
                case 'type':
                    badge = 'type';    cls = 'rec-type-type';
                    detail = `${this._esc(s.target.value)} ← <span class="arg">${this._esc(s.value)}</span>`;
                    break;
                case 'select':
                    badge = 'select';  cls = 'rec-type-select';
                    detail = `${this._esc(s.target.value)} ← <span class="arg">${this._esc(s.value)}</span>`;
                    break;
                case 'wait':
                    badge = 'wait';    cls = 'rec-type-wait';
                    detail = `<span class="arg">${this._esc(s.ms)} ms</span>`;
                    break;
                case 'wait_for_text':
                    badge = 'text';    cls = 'rec-type-text';
                    detail = `${this._esc(s.target.value)} ⊃ <span class="arg">"${this._esc(s.contains)}"</span>`;
                    break;
                default:
                    badge = s.type;    cls = '';
                    detail = this._esc(JSON.stringify(s));
            }
            return `<div class="rec-step-line">
                <span class="rec-step-num">${i + 1}</span>
                <span class="rec-step-type ${cls}">${badge}</span>
                <span class="rec-step-detail">${detail}</span>
            </div>`;
        };

        cont.innerHTML = header + this.steps.map(filaPara.bind(this)).join('');
        cont.classList.add('show');
    }

    _showSuccess(msg) {
        if (!this.ui.success) return;
        const el = document.getElementById(this.ui.success);
        if (!el) return;
        const txt = document.getElementById(this.ui.successText);
        if (txt) txt.textContent = msg;
        el.classList.add('show');
    }

    _hideSuccess() {
        if (!this.ui.success) return;
        document.getElementById(this.ui.success)?.classList.remove('show');
    }

    _setEnabled(id, enabled) {
        const el = document.getElementById(id);
        if (!el) return;
        el.disabled = !enabled;
    }

    start() {
        this.steps = [];
        this.recording = true;
        // capture=true para no perder el último click si el form hace stopPropagation.
        document.addEventListener('click', this._onClick, true);
        document.addEventListener('input', this._onInput, true);
        document.addEventListener('change', this._onChange, true);
        this._setStatus('active', 'Grabando…');
        this._setEnabled(this.ui.start, false);
        this._setEnabled(this.ui.stop, true);
        this._setEnabled(this.ui.download, false);
        this._hideSuccess();
        this._renderSteps();
        this._refreshCount();
    }

    stop() {
        this.recording = false;
        document.removeEventListener('click', this._onClick, true);
        document.removeEventListener('input', this._onInput, true);
        document.removeEventListener('change', this._onChange, true);
        // wait_for_text del toast: sin esto el runner cierra antes de que aparezca.
        this.steps.push({
            type: 'wait_for_text',
            target: { by: 'css', value: '#toast' },
            contains: 'Guardado',
        });
        this._setStatus('success', 'Grabación lista');
        this._setEnabled(this.ui.stop, false);
        this._setEnabled(this.ui.download, true);
        this._setEnabled(this.ui.start, true);
        this._refreshCount();
        this._showSuccess(`Workflow grabado con ${this.steps.length} ${this.steps.length === 1 ? 'paso' : 'pasos'}. Pulsa Download para guardar.`);
        this._renderSteps();
    }

    download() {
        // wait inicial: en otra ejecución el primer click no cae sobre página a medio renderizar.
        const workflow = { ...this.meta, steps: [{ type: 'wait', ms: 500 }, ...this.steps] };
        const blob = new Blob([JSON.stringify(workflow, null, 2)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `${this.meta.id}.workflow.json`;
        a.click();
        // Confirma que se ha descargado: importante en demos para que el
        // espectador vea claro que algo ha pasado al pulsar Download.
        this._showSuccess(`Descargado ${this.meta.id}.workflow.json (${this.steps.length} pasos).`);
    }
}

// Ids comunes del panel del recorder (los 3 HTMLs reusan el mismo HTML
// del panel y por tanto los mismos ids). Se exporta para que la
// inicialización inline de cada página no tenga que duplicarlos.
window.RECORDER_UI_DEFAULTS = {
    start: 'btn_start',
    stop: 'btn_stop',
    download: 'btn_download',
    indicator: 'rec_indicator',
    statusText: 'rec_status_text',
    count: 'step_count',
    success: 'rec_success',
    successText: 'rec_success_text',
    stepsList: 'rec_steps',
};

// La instancia concreta del recorder se crea en cada HTML con su metadata
// y placeholders propios (alta, baja, actualización de stock).
window.FormRecorder = FormRecorder;
