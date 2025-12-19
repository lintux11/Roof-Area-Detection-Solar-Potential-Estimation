import { useState } from 'react';
import { FileUploader } from './components/FileUploader';
import { RoofMaskOverlay } from './components/RoofMaskOverlay';
import { StatsCard } from './components/StatsCard';
import { uploadImage, segmentImage, calculateArea, estimatePanels, type Report } from './api';
import { Sun, Download, RefreshCw } from 'lucide-react';
import './App.css';

function App() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'upload' | 'processing' | 'result'>('upload');
  const [opacity, setOpacity] = useState(0.5);
  const [viewMode, setViewMode] = useState<'mask' | 'panels'>('mask');

  const handleUpload = async (file: File) => {
    try {
      setLoading(true);
      const uploadedReport = await uploadImage(file);
      setReport(uploadedReport);
      setStep('processing');

      const segmentedReport = await segmentImage(uploadedReport.id);
      setReport(segmentedReport);

      const calculatedReport = await calculateArea(segmentedReport.id);
      setReport(calculatedReport);

      const finalReport = await estimatePanels(calculatedReport.id);
      setReport(finalReport);

      setStep('result');
    } catch (error: any) {
      console.error("Error processing image:", error);
      const errorMessage = error.response?.data?.detail || error.message || "Unknown error";
      alert(`Failed to process image: ${errorMessage}`);
      setStep('upload');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setReport(null);
    setStep('upload');
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="container header-content">
          <div className="flex items-center">
            <div className="logo-container">
              <Sun size={24} color="#0ea5e9" />
            </div>
            <h1 className="logo-text">
              SolarRoof AI
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500 }}>Documentation</a>
            <button className="btn btn-dark">
              Get API Key
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container" style={{ padding: '3rem 1rem' }}>
        <div className="text-center mb-12">
          <h2 className="text-4xl mb-4">
            Instant Roof Area & Solar Potential
          </h2>
          <p className="text-lg text-slate-600" style={{ maxWidth: '42rem', margin: '0 auto' }}>
            Upload a satellite or drone image to automatically detect roof area and estimate solar panel capacity using advanced AI.
          </p>
        </div>

        {step === 'upload' && (
          <div style={{ maxWidth: '36rem', margin: '0 auto' }}>
            <FileUploader onUpload={handleUpload} isUploading={loading} />
          </div>
        )}

        {step === 'processing' && (
          <div className="text-center" style={{ padding: '5rem 0', maxWidth: '36rem', margin: '0 auto' }}>
            <div className="spinner mb-4"></div>
            <h3 className="text-lg font-medium">Analyzing Roof Structure...</h3>
            <p className="text-slate-500" style={{ marginTop: '0.5rem' }}>Running DeepLabV3 segmentation model</p>
          </div>
        )}

        {step === 'result' && report && (
          <div className="grid gap-8 lg-grid-cols-3">
            {/* Left Column: Image & Controls */}
            <div className="lg-col-span-2 space-y-6">
              <div className="card" style={{ padding: '0.5rem', overflow: 'hidden' }}>
                {viewMode === 'mask' ? (
                  <RoofMaskOverlay
                    imageUrl={report.image_path}
                    maskUrl={report.mask_path}
                    opacity={opacity}
                  />
                ) : (
                  <div style={{ position: 'relative', width: '100%', height: '500px', backgroundColor: '#f1f5f9', borderRadius: '0.5rem', overflow: 'hidden' }}>
                    <img
                      src={`http://localhost:8000/static/${report.panel_layout_path?.replace('app/data/', '')}`}
                      alt="Panel Layout"
                      style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                    />
                  </div>
                )}
              </div>

              <div className="card">
                <div className="flex justify-between mb-4">
                  <div className="flex space-x-2">
                    <button
                      className={`btn ${viewMode === 'mask' ? 'btn-primary' : 'btn-secondary'}`}
                      onClick={() => setViewMode('mask')}
                    >
                      Roof Mask
                    </button>
                    {report.panel_layout_path && (
                      <button
                        className={`btn ${viewMode === 'panels' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setViewMode('panels')}
                      >
                        Panel Layout
                      </button>
                    )}
                  </div>
                </div>

                {viewMode === 'mask' && (
                  <>
                    <div className="flex justify-between mb-2">
                      <label className="font-medium text-sm">Mask Opacity</label>
                      <span className="text-sm text-slate-500">{Math.round(opacity * 100)}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={opacity}
                      onChange={(e) => setOpacity(parseFloat(e.target.value))}
                    />
                  </>
                )}
              </div>
            </div>

            {/* Right Column: Stats & Actions */}
            <div className="space-y-6">
              <div className="grid gap-4">
                <StatsCard
                  label="Total Roof Area"
                  value={report.total_area?.toFixed(1) || 0}
                  unit="m²"
                  icon="area"
                />
                <StatsCard
                  label="Usable Solar Area"
                  value={report.usable_area?.toFixed(1) || 0}
                  unit="m²"
                  icon="area"
                />
                <StatsCard
                  label="Max Panels"
                  value={report.panel_count || 0}
                  unit="panels"
                  icon="panels"
                />
                <StatsCard
                  label="Est. Capacity"
                  value={report.solar_capacity?.toFixed(2) || 0}
                  unit="kW"
                  icon="power"
                />
              </div>

              <div className="flex flex-col space-y-4">
                <button className="btn btn-primary" style={{ width: '100%', padding: '0.75rem' }}>
                  <Download size={20} />
                  <span>Download Full Report</span>
                </button>
                <button
                  onClick={handleReset}
                  className="btn btn-secondary" style={{ width: '100%', padding: '0.75rem' }}
                >
                  <RefreshCw size={20} />
                  <span>Analyze Another Image</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
