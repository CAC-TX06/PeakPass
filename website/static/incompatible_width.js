// If the screen width is less than 1080px, then redirect to the /incompatible-width page
// This is to prevent the website from being displayed on mobile devices

if (screen.width < 1080) {
    window.location.href = "/incompatible_width";
}