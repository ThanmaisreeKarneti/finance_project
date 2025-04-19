document.addEventListener("DOMContentLoaded", function () {
    const dataDiv = document.getElementById("profit-loss-data");
  
    const profit = parseFloat(dataDiv.dataset.profit);
    const loss = parseFloat(dataDiv.dataset.loss);
  
    const rings = [
      { id: 'profit-ring', percent: profit, color: 'green' },
      { id: 'loss-ring', percent: loss, color: 'red' }
    ];
  
    rings.forEach(({ id, percent, color }) => {
      const circle = document.getElementById(id);
      if (circle) {
        const radius = circle.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
  
        circle.style.strokeDasharray = `${circumference}`;
        circle.style.strokeDashoffset = `${circumference}`;
        circle.style.stroke = color;
  
        const offset = circumference - (percent / 100) * circumference;
        circle.style.strokeDashoffset = offset;
      }
    });
  });
  