import { useState } from 'react'

export default function ApplicationForm({ projectId, onSubmit, onCancel, isLoading }) {
  const [formData, setFormData] = useState({
    project: projectId,
    applicant_name: '',
    applicant_email: '',
    applicant_phone: '',
    applicant_portfolio: '',
    applicant_skills: [],
    cover_letter: '',
  })
  const [skillInput, setSkillInput] = useState('')
  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }))
    }
  }

  const handleAddSkill = () => {
    if (skillInput.trim() && !formData.applicant_skills.includes(skillInput.trim())) {
      setFormData((prev) => ({
        ...prev,
        applicant_skills: [...prev.applicant_skills, skillInput.trim()],
      }))
      setSkillInput('')
    }
  }

  const handleRemoveSkill = (skill) => {
    setFormData((prev) => ({
      ...prev,
      applicant_skills: prev.applicant_skills.filter((s) => s !== skill),
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Validation
    const newErrors = {}
    if (!formData.applicant_name.trim()) {
      newErrors.applicant_name = 'Name is required'
    }
    if (!formData.applicant_email.trim()) {
      newErrors.applicant_email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.applicant_email)) {
      newErrors.applicant_email = 'Invalid email format'
    }
    if (!formData.cover_letter.trim()) {
      newErrors.cover_letter = 'Cover letter is required'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="applicant_name" className="block text-sm font-medium text-gray-700">
          Full Name *
        </label>
        <input
          type="text"
          id="applicant_name"
          name="applicant_name"
          value={formData.applicant_name}
          onChange={handleChange}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
            errors.applicant_name ? 'border-red-300' : ''
          }`}
          required
        />
        {errors.applicant_name && (
          <p className="mt-1 text-sm text-red-600">{errors.applicant_name}</p>
        )}
      </div>

      <div>
        <label htmlFor="applicant_email" className="block text-sm font-medium text-gray-700">
          Email Address *
        </label>
        <input
          type="email"
          id="applicant_email"
          name="applicant_email"
          value={formData.applicant_email}
          onChange={handleChange}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
            errors.applicant_email ? 'border-red-300' : ''
          }`}
          required
        />
        {errors.applicant_email && (
          <p className="mt-1 text-sm text-red-600">{errors.applicant_email}</p>
        )}
      </div>

      <div>
        <label htmlFor="applicant_phone" className="block text-sm font-medium text-gray-700">
          Phone Number
        </label>
        <input
          type="tel"
          id="applicant_phone"
          name="applicant_phone"
          value={formData.applicant_phone}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <div>
        <label htmlFor="applicant_portfolio" className="block text-sm font-medium text-gray-700">
          Portfolio URL
        </label>
        <input
          type="url"
          id="applicant_portfolio"
          name="applicant_portfolio"
          value={formData.applicant_portfolio}
          onChange={handleChange}
          placeholder="https://yourportfolio.com"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Skills</label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={skillInput}
            onChange={(e) => setSkillInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSkill())}
            placeholder="Add a skill"
            className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
          <button
            type="button"
            onClick={handleAddSkill}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 text-sm"
          >
            Add
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {formData.applicant_skills.map((skill, idx) => (
            <span
              key={idx}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
            >
              {skill}
              <button
                type="button"
                onClick={() => handleRemoveSkill(skill)}
                className="ml-2 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      <div>
        <label htmlFor="cover_letter" className="block text-sm font-medium text-gray-700">
          Cover Letter *
        </label>
        <textarea
          id="cover_letter"
          name="cover_letter"
          rows={6}
          value={formData.cover_letter}
          onChange={handleChange}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
            errors.cover_letter ? 'border-red-300' : ''
          }`}
          placeholder="Tell us why you're a good fit for this project..."
          required
        />
        {errors.cover_letter && (
          <p className="mt-1 text-sm text-red-600">{errors.cover_letter}</p>
        )}
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Submitting...' : 'Submit Application'}
        </button>
      </div>
    </form>
  )
}
