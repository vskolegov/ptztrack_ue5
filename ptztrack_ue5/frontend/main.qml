import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Dialogs
import QtQml
import QtQuick.Layouts
import QtMultimedia
import QtQuick.Controls.Material


ApplicationWindow {
    width: 800
    height: 600
    visible: true

    property bool loader_bool: false
    property bool scene_selected: false

    Loader {
            id: mainLoader
            visible: loader_bool
            anchors.fill: parent
            property int loader_prop_index
            onLoaded: console.log("page is loaded: ", source)
        }

    Control {
        padding: 20
        anchors.top: !loader_bool ? parent.top : mainLoader.bottom
        contentItem: Column {
            spacing: 20
            Row {
                spacing: 20
                
                Button { visible: scene_selected; text: "Add Camera"; onClicked: { navigate("addCamera"); loader_bool = !loader_bool }}
                Button { text: "Choise Scene"; onClicked: { PTZCameras.get_scenes(); navigate("choiseScene"); loader_bool = !loader_bool; scene_selected = true }}
                /* Button { visible: scene_selected; text: "Edit Scene"; onClicked: { navigate("editScene"); loader_bool = !loader_bool }} */
                Button { text: "Add Scene"; onClicked: { navigate("addScene"); loader_bool = !loader_bool; scene_selected = true }}

            }

            Repeater {
                model: PTZCameras.camera_keys
                id: ptzCameraSettings


                Column {
                        spacing: 8
                        RowLayout {
                            RowLayout {
                                //Label { text: "Camera " + (index + 1) }
                                TextField { id: socket_Field; text: model.modelData; }
                            }
                            
                            Button {
                                text: "Remove"
                                onClicked: {
                                    PTZCameras.removeItem(model.modelData)
                                }
                            }

                            Button {
                                text: "Edit"
                                onClicked: {
                                    PTZCameras.edit_camera(model.modelData, socket_Field.text)
                                }
                            }
                        }
                    }

            }

            Button {
                visible: scene_selected;
                text: "Initialize cameras"
                onClicked: {
                    PTZCameras.initialize_cameras()
                }
            }
        }
    }
    
    RowLayout {
        visible: scene_selected
        anchors.bottom: parent.bottom
        anchors.left: parent.left

        Text {
            text: PTZCameras.scene_current + " is selected"
            font.family: "Helvetica"
            font.pointSize: 16
        }

        Button {
            text: "Start Scene"
            onClicked: { PTZCameras.start_scene() }
        }

        Button {
            text: "Stop Scene"
            onClicked: { PTZCameras.stop_scene() }
        }
    }

    Button {
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        text: "Settings"
        onClicked: { navigate("settings"); loader_bool = !loader_bool }
    }

        function applySettings(ip, port, unreal) {
            PTZCameras.store(ip, port, unreal)
        }

        function applyScene(scene) {
            PTZCameras.load_scene(scene)
        }

        function applyNewScene(scene) {
            PTZCameras.add_new_scene(scene)
        }

        function navigate(page) {
            mainLoader.source = page + ".qml"
        }
}
