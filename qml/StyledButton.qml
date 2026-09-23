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
    color: !enabled
        ? backend.colorBorder
        : (mouseArea.pressed ? buttonColor : (mouseArea.containsMouse ? Qt.lighter(buttonColor, 1.15) : buttonColor))
    border.width: enabled ? 0 : 1
    border.color: backend.colorTextSecondary

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
            id: iconImg
            source: root.icon
            sourceSize.width: 18
            sourceSize.height: 18
            visible: false
        }
        ColorOverlay {
            anchors.verticalCenter: parent.verticalCenter
            visible: root.icon !== ""
            width: 18
            height: 18
            source: iconImg
            color: root.enabled ? backend.colorOnAccent : backend.colorTextSecondary
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: root.label
            color: root.enabled ? backend.colorOnAccent : backend.colorTextSecondary
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
