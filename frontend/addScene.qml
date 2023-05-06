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
        Label { text: "Add Scene" }
        TextField {
            id: sceneField;
            placeholderText: "Scene name";
            text: "";
        }
    }
    Button {
        text: "Apply"
        onClicked: {
            applyNewScene(sceneField.text);
            loader_bool = !loader_bool;
            console.log('scene: ' + sceneField.text + ' added!')
        }
    }
}