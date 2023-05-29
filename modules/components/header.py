import gradio as gr

from modules import model_manager, vae


def ui():
    model_list_str = lambda: [x.model_id for x in model_manager.sd_models]
    model_id = (
        lambda: model_manager.sd_model.model_id
        if model_manager.sd_model is not None
        else None
    )

    with gr.Box():
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Row():
                    with gr.Row():
                        model_id_dropdown = gr.Dropdown(
                            value=model_id(),
                            choices=model_list_str(),
                            show_label=False,
                        )
                        reload_models_button = gr.Button(
                            "🔄", elem_classes=["tool-button"]
                        )
                    with gr.Row() as add_model_group:
                        add_model_textbox = gr.Textbox(
                            placeholder="Add model",
                            show_label=False,
                        )
                        add_model_button = gr.Button("💾", elem_classes=["tool-button"])
                    with gr.Row():
                        vae_id_dropdown = gr.Dropdown(
                            placeholder="VAE",
                            choices=vae.list_vae_models() + ["Auto"],
                            value="Auto",
                            show_label=False,
                        )
                        reload_vae_button = gr.Button("🔄", elem_classes=["tool-button"])
            with gr.Row():
                mode = gr.Radio(
                    choices=model_manager.sd_model.available_modes(),
                    value=model_manager.sd_model.mode,
                    show_label=False,
                )
                reload_mode_button = gr.Button(
                    "🔄",
                    elem_classes=["tool-button"],
                    elem_id="inference-mode-reload-button",
                )

    def change_model(model_id: str):
        if model_id not in model_list_str():
            raise ValueError("Model not found.")
        model_manager.set_model(model_id)
        return model_manager.sd_model.model_id, gr.Radio.update(
            value=model_manager.sd_model.mode,
            choices=model_manager.sd_model.available_modes(),
        )

    def reload_models():
        model_manager.reload_models()
        return (
            gr.Dropdown.update(choices=model_list_str(), value=model_id()),
            model_manager.sd_model.mode,
        )

    model_id_dropdown.change(
        fn=change_model, inputs=[model_id_dropdown], outputs=[model_id_dropdown, mode]
    )
    reload_models_button.click(
        fn=reload_models,
        outputs=[model_id_dropdown, mode],
    )

    def change_vae(name):
        file_path = vae.resolve_vae(name) if name != "Auto" else None
        model_manager.sd_model.pipe.swap_vae(file_path)
        return name

    def reload_vae():
        return gr.Dropdown.update(
            choices=vae.list_vae_models(), value=vae_id_dropdown.value
        )

    vae_id_dropdown.change(
        fn=change_vae, inputs=[vae_id_dropdown], outputs=[vae_id_dropdown]
    )
    reload_vae_button.click(
        fn=reload_vae,
        outputs=[vae_id_dropdown],
    )

    def add_model(model_id):
        if model_id not in model_list_str():
            searched = model_manager.search_model(model_id)
            if len(searched) < 1:
                raise ValueError("Model not found.")
            model_manager.add_model(model_id)
        return gr.Dropdown.update(choices=model_list_str())

    add_model_button.click(
        fn=add_model, inputs=[add_model_textbox], outputs=[model_id_dropdown]
    )

    def on_mode_change(mode: str):
        model_manager.sd_model.change_mode(mode)
        return (
            model_manager.sd_model.mode,
            gr.Group.update(visible=model_manager.sd_model.mode == "diffusers"),
        )

    mode.change(
        fn=on_mode_change,
        inputs=[mode],
        outputs=[mode, add_model_group],
    )

    reload_mode_button.click(
        fn=lambda: gr.Radio.update(
            value=model_manager.sd_model.mode,
            choices=model_manager.sd_model.available_modes(),
        ),
        inputs=[],
        outputs=[mode],
    )
