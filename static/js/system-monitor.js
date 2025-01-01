function updateSystemStats() {
    fetch('/get_system_stats')
        .then(response => response.json())
        .then(data => {
            // Get all stat items
            const statItems = document.querySelectorAll('.stat-item');
            
            statItems.forEach(item => {
                const strongText = item.querySelector('strong').textContent;
                
                // CPU Temperature
                if (strongText === 'CPU Temperature:') {
                    item.querySelector('span').textContent = data.cpu_temp;
                }
                
                // CPU Usage
                else if (strongText === 'CPU Usage:') {
                    const progressBar = item.querySelector('.progress-bar');
                    const progressText = item.querySelector('.progress-text');
                    const cpuValue = parseFloat(data.cpu_usage);
                    progressBar.style.width = cpuValue + '%';
                    progressText.textContent = data.cpu_usage;
                }
                
                // Memory
                else if (strongText === 'Memory:') {
                    const progressBar = item.querySelector('.progress-bar');
                    const progressText = item.querySelector('.progress-text');
                    const memValue = parseFloat(data.memory_percent);
                    progressBar.style.width = memValue + '%';
                    progressText.textContent = data.memory_used + ' / ' + data.memory_total;
                }
            });
            
            // Debug log
            console.log('Updated stats:', data);
        })
        .catch(error => console.error('Error fetching stats:', error));
}

// Update every 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    // Run once immediately
    updateSystemStats();
    // Then every 5 seconds
    setInterval(updateSystemStats, 5000);
});