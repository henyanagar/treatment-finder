import ClinicSearch from './ClinicSearch'
import SmartSearch from './SmartSearch'

/**
 * Landing hero section that hosts AI and standard search panels.
 * @param {{onAiResult: (result: object | null) => void, onSearchResults: (results: Array<object>) => void}} props
 */
function Hero({ onAiResult, onSearchResults }) {
  return (
    <section id="hero" className="mx-auto max-w-6xl px-6 pb-8 pt-10">
      <div className="mx-auto max-w-4xl text-center">
        <h1 className="text-4xl font-semibold tracking-tight text-slate-800 sm:text-5xl">
          Discover Your Perfect Aesthetic Treatment
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-500">
          Let our AI guide you to the best treatments and clinics tailored to your
          unique needs.
        </p>
      </div>

      <div className="mx-auto mt-8 rounded-3xl border border-slate-200 bg-[#F8FAFC] p-6 shadow-sm sm:p-8">
        <SmartSearch onResult={onAiResult} />
        <div className="my-5 border-t border-slate-200 text-center text-sm text-slate-400">or</div>
        <ClinicSearch onResults={onSearchResults} />
      </div>
    </section>
  )
}

export default Hero
