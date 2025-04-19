document.querySelector('.get-started-btn').addEventListener('click', function() {
    const name = document.getElementById('name').value;
    const mobile = document.getElementById('mobile').value;
    const location = document.getElementById('location').value || document.getElementById('manual-location').value;
    const primaryCrop = document.getElementById('primary-crop').value;
    const growthStage = document.getElementById('growth-stage').value;
    const challenges = Array.from(document.querySelectorAll('.challenge-btn'))
        .filter(btn => btn.style.backgroundColor === 'rgb(165, 214, 167)')
        .map(btn => btn.textContent);

    if (name && mobile && location && primaryCrop && growthStage) {
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                mobile: mobile,
                location: location,
                primaryCrop: primaryCrop,
                growthStage: growthStage,
                challenges: challenges
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/chat';
            } else {
                alert(data.message);
            }
        })
        .catch(error => alert('Error logging in.'));
    } else {
        alert('Please fill all required fields.');
    }
});

document.querySelectorAll('.challenge-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        this.style.backgroundColor = this.style.backgroundColor === 'rgb(165, 214, 167)' ? '#fff' : '#a5d6a7';
    });
});

document.getElementById('location').addEventListener('change', function() {
    const manualInput = document.getElementById('manual-location');
    if (this.value === '') {
        manualInput.style.display = 'block';
    } else {
        manualInput.style.display = 'none';
    }
});