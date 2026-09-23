import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

// Left panel: title, model selection, action buttons, tips card.
// Replaces BackgroundRemoverApp._create_control_panel + _create_tips_card.
// No hardcoded colors/icons/strings: everything comes from `backend`
// (utils/constants.py, utils/icons.py, utils/strings.py).
Rectangle {
    id: root

    signal uploadRequested()
    signal saveRequested()

    radius: 20
    gradient: Gradient {
        orientation: Gradient.Vertical
        GradientStop { position: 0.0; color: backend.colorSurface }
        GradientStop { position: 1.0; color: backend.colorSurfaceDark }
    }

    layer.enabled: true
    layer.effect: DropShadow {
        horizontalOffset: 0
        verticalOffset: 10
        radius: 40
        samples: 41
        color: backend.colorPanelShadow
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Image {
                id: titleIcon
                source: backend.iconApp
                sourceSize.width: 24
                sourceSize.height: 24
                visible: false
            }
            ColorOverlay {
                width: titleIcon.width
                height: titleIcon.height
                source: titleIcon
                color: backend.colorPrimary
            }
            Label {
                text: backend.stringAppTitle
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                font.pixelSize: 22
                font.bold: true
                color: backend.colorText
            }
        }

        Label {
            text: backend.stringAppSubtitle
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            font.pixelSize: 12
            color: backend.colorTextSecondary
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: backend.colorBorder
        }

        Label {
            text: backend.stringModelLabel
            font.pixelSize: 12
            font.bold: true
            color: backend.colorText
        }

        ComboBox {
            id: modelCombo
            Layout.fillWidth: true
            Layout.minimumHeight: 35
            model: backend.availableModels
            currentIndex: 0
            onActivated: backend.setCurrentModel(currentText)

            background: Rectangle {
                implicitHeight: 35
                radius: 10
                color: backend.colorSurface
                border.width: 2
                border.color: modelCombo.hovered ? backend.colorPrimary : backend.colorBorder
            }
            contentItem: Text {
                text: modelCombo.displayText
                color: backend.colorText
                leftPadding: 16
                verticalAlignment: Text.AlignVCenter
                font.pixelSize: 14
            }
            popup: Popup {
                y: modelCombo.height
                width: modelCombo.width
                padding: 5
                contentItem: ListView {
                    clip: true
                    implicitHeight: contentHeight
                    model: modelCombo.popup.visible ? modelCombo.delegateModel : null
                    currentIndex: modelCombo.highlightedIndex
                }
                background: Rectangle {
                    color: backend.colorSurface
                    border.color: backend.colorBorder
                    border.width: 2
                    radius: 8
                }
            }
            delegate: ItemDelegate {
                width: modelCombo.width
                highlighted: modelCombo.highlightedIndex === index
                contentItem: Text {
                    text: modelData
                    color: backend.colorText
                    font.pixelSize: 13
                    verticalAlignment: Text.AlignVCenter
                    leftPadding: 8
                }
                background: Rectangle {
                    color: highlighted ? backend.colorSurfaceLight : "transparent"
                }
            }
        }

        StyledButton {
            Layout.fillWidth: true
            label: backend.stringButtonUpload
            icon: backend.iconUpload
            buttonColor: backend.colorPrimary
            onClicked: root.uploadRequested()
        }

        StyledButton {
            Layout.fillWidth: true
            label: backend.stringButtonRemoveBg
            icon: backend.iconRemoveBg
            buttonColor: backend.colorAccent
            enabled: backend.canProcess
            onClicked: backend.processImage()
        }

        StyledButton {
            Layout.fillWidth: true
            label: backend.stringButtonSave
            icon: backend.iconSave
            buttonColor: backend.colorSuccess
            enabled: backend.canSave
            onClicked: root.saveRequested()
        }

        Rectangle {
            Layout.fillWidth: true
            radius: 12
            color: backend.colorTipsBackground
            border.color: backend.colorTipsBorder
            border.width: 1
            implicitHeight: tipsColumn.implicitHeight + 36

            ColumnLayout {
                id: tipsColumn
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 18
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Image {
                        id: tipIcon
                        source: backend.iconTip
                        sourceSize.width: 16
                        sourceSize.height: 16
                        visible: false
                    }
                    ColorOverlay {
                        width: tipIcon.width
                        height: tipIcon.height
                        source: tipIcon
                        color: backend.colorPrimary
                    }
                    Label {
                        text: backend.stringTipsTitle
                        font.pixelSize: 14
                        font.bold: true
                        color: backend.colorPrimary
                    }
                }
                Label {
                    text: backend.stringTipsText
                    textFormat: Text.RichText
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                    font.pixelSize: 13
                    color: backend.colorText
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
