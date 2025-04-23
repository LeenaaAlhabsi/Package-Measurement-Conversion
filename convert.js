document.getElementById('convert').onclick = async function() {
    const input = document.getElementById('inputString').value.trim();
    const result = document.getElementById('result');
    result.className = '';
    result.textContent = 'Converting...';

    if (!input) {
        result.textContent = 'Please enter a measurement string.';
        result.className = 'error';
        return;
    }

    try {
        const response = await fetch(`http://localhost:8080/convert-measurements?input=${encodeURIComponent(input)}`);
        if (!response.ok) {
            throw new Error('Server error or invalid input.');
        }
        const data = await response.json();
        if (data.processed !== undefined) {
            result.textContent = `[${data.processed.join(', ')}]`;
            result.className = '';
        } else {
            result.textContent = data.error ? data.error : 'Unexpected response from server.';
            result.className = 'error';
        }
    } catch (err) {
        result.textContent = 'Could not connect to server or invalid response.';
        result.className = 'error';
    }
};

document.getElementById('history').onclick = async function() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '';
    try {
        const response = await fetch('http://localhost:8080/history');
        if (!response.ok) throw new Error();
        const data = await response.json();
        if (data.history && data.history.length > 0) {
            data.history.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `Input: ${item.sequence} → Output: [${item.processed.join(', ')}]`;
                historyList.appendChild(li);
            });
        } else {
            historyList.innerHTML = '<li>No history found.</li>';
        }
    } catch {
        historyList.innerHTML = '<li class="error">Could not fetch history.</li>';
    }
};

document.getElementById('clearResult').onclick = function() {
    document.getElementById('result').textContent = '';
    document.getElementById('result').className = '';
};

document.getElementById('clearHistory').onclick = function() {
    document.getElementById('historyList').innerHTML = '';
};