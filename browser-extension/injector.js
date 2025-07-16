(function() {
	const scriptEl = document.createElement("script");
	scriptEl.src = chrome.runtime.getURL("injected.js");
  
	scriptEl.addEventListener("load", function() {
		this.remove();
	});
  
	(document.head || document.documentElement).append(scriptEl);
})();