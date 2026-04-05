import { app } from "../../scripts/app.js";

const TARGET_CLASS = "ArataShotTxtExport";

function triggerDownload(fileInfo) {
    if (!fileInfo?.relative_output_path) {
        return;
    }

    const anchor = document.createElement("a");
    anchor.href = `/arata-transnetv2/download?path=${encodeURIComponent(fileInfo.relative_output_path)}`;
    anchor.download = fileInfo.filename || "shots.txt";
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
}

function updateButton(widget, fileInfo, emptyLabel) {
    widget.name = fileInfo ? `Download ${fileInfo.filename}` : emptyLabel;
}

app.registerExtension({
    name: "arata.transnetv2.download_buttons",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== TARGET_CLASS && nodeType.comfyClass !== TARGET_CLASS) {
            return;
        }

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = onNodeCreated?.apply(this, arguments);
            this._arataBoundaryFiles = [];

            this._arataShotsButton = this.addWidget("button", "Download shots JSON", null, () => {
                const fileInfo = this._arataBoundaryFiles.find((item) => item.label === "shots");
                triggerDownload(fileInfo);
            });

            this._arataStatusWidget = this.addWidget(
                "text",
                "export_status",
                "Run the node to generate the shots JSON file.",
                () => {}
            );
            this.size = [Math.max(this.size[0], 340), this.size[1]];
            return result;
        };

        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);

            const files = Array.isArray(message?.boundary_files)
                ? message.boundary_files
                : Array.isArray(message?.ui?.boundary_files)
                    ? message.ui.boundary_files
                    : [];
            this._arataBoundaryFiles = files;

            const shotsFile = files.find((item) => item.label === "shots");
            updateButton(this._arataShotsButton, shotsFile, "Download shots JSON");

            if (this._arataStatusWidget) {
                this._arataStatusWidget.value = shotsFile
                    ? `Ready: ${shotsFile.filename}`
                    : "No shots file was exported.";
            }
            this.setDirtyCanvas(true, true);
        };
    },
});
