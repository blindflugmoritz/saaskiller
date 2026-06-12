import '@testing-library/jest-dom';

// jsdom doesn't implement execCommand — provide a stub so tests can spy on it
if (!document.execCommand) {
	(document as unknown as { execCommand: () => boolean }).execCommand = () => false;
}
