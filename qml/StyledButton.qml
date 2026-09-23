import QtQuick
import Qt5Compat.GraphicalEffects

// Reusable button: replaces ComponentBuilder.create_button (Builder pattern
// widget construction is now plain QML component composition).
// No hardcoded colors: every color comes from the central `backend` bridge
// (utils/constants.py is the single source of truth).
Rectangle {
    id: root

    property string label: ""
    property string icon: ""
    property color buttonColor: backend.colorPrimary

    signal clicked()

    implicitHeight: 48
    radius: 12
    opacity: enabled ? 1.0 : 0.6
    color: !enabled
        ? backend.colorSurfaceLight
        : (mouseArea.pressed ? buttonColor : (mouseArea.containsMouse ? Qt.lighter(buttonColor, 1.15) : buttonColor))

    layer.enabled: true
    layer.effect: DropShadow {
        horizontalOffset: 0
        verticalOffset: 4
        radius: 15
        samples: 17
        color: backend.colorButtonShadow
    }

    Row {
        anchors.centerIn: parent
        spacing: 8

        Image {
            anchors.verticalCenter: parent.verticalCenter
            visible: root.icon !== ""
            source: root.icon
            sourceSize.width: 18
            sourceSize.height: 18
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: root.label
            color: root.enabled ? backend.colorText : backend.colorTextSecondary
            font.pixelSize: 14
            font.bold: true
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: root.clicked()
    }
}
