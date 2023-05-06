import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Dialogs
import QtQml
import QtQuick.Layouts
import QtMultimedia
import QtQuick.Controls.Material


Column {
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    padding: 20
    RowLayout {
        Label { text: "Add camera" }
        TextField {
            id: ipField;
            placeholderText: "IP address";
            text: "";
        }
        TextField { id: portField; placeholderText: "Port"; text: "" }
        TextField { id: unrealNameField; placeholderText: "Unreal camera name"; text: "" }
    }
    Button {
        text: "Apply"
        onClicked: {
            applySettings(ipField.text, portField.text, unrealNameField.text);
            loader_bool = !loader_bool;
            console.log(PTZCameras.cameras)
        }
    }
}