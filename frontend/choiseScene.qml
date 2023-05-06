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

    ComboBox {
    id: sceneDropdown
    model: PTZCameras.scene_keys
    }
    

    Button {
        text: "Apply"
        onClicked: {
            loader_bool = !loader_bool;
            applyScene(sceneDropdown.currentText)
        }
    }
}